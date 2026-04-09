from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from core.scheduler import scheduler

from repository.assignment_repo import AssignmentRepository
from dependencies import get_session
from repository.course_repo import CourseRepository
from services.assignment_service import get_assignment_detail_with_questions, publish_assignment_to_class, \
    get_class_assignments_logic, end_class_assignment_logic, get_class_assignment_detail_logic
from services.course_service import get_course_classes_logic, get_class_students_logic
from services.scheduler_tasks import async_close_assignment_logic

# 定义路由，前缀设为 /teacher
router = APIRouter(prefix="/teacher", tags=["teacher"])


@router.get("/{user_id}/assignments")
async def get_teacher_assignments(
        user_id: int,
        db: AsyncSession = Depends(get_session)
):
    """
    根据教师ID 查询该教师的所有草稿作业
    """
    assignments = await AssignmentRepository.get_assignments_by_user_id(db, user_id)
    if not assignments:
        return {"code": 200, "message": "暂无作业记录", "data": []}
    data = []
    for a in assignments:
        formatted_deadline = a.deadline.strftime("%Y-%m-%d %H:%M") if a.deadline else None
        formatted_created_at = a.created_at.strftime("%Y-%m-%d %H:%M") if hasattr(a,'created_at') and a.created_at else None
        data.append({
            "assignment_id": a.id,
            "user_id": a.user_id,
            "title": a.title,
            "deadline": formatted_deadline,
            "created_at": formatted_created_at,
            "q_count":a.q_count
        })
    return {
        "code": 200,
        "message": "查询成功",
        "data": data
    }

@router.get("/{assignment_id}/detail")
async def get_assignment_detail(
        assignment_id: int,
        db: AsyncSession = Depends(get_session)
):
    """
    根据草稿作业ID一股脑返回所有题目详情
    """
    data = await get_assignment_detail_with_questions(db, assignment_id)

    if not data:
        # 如果找不到该作业，返回 404
        raise HTTPException(status_code=404, detail="未找到该作业草稿")

    return {
        "code": 200,
        "message": "详情查询成功",
        "data": data
    }


@router.get("/{user_id}/course")
async def get_teacher_courses(
        user_id: int,
        db: AsyncSession = Depends(get_session)
):
    """
    根据教师 ID 获取其关联的课程信息
    """
    courses = await CourseRepository.get_courses_by_teacher_id(db, user_id)
    if not courses:
        return {
            "code": 200,
            "message": "该教师暂无关联课程",
            "data": []
        }
    data = [
        {
            "course_id": c.course_id,
            "course_name": c.course_name
        }
        for c in courses
    ]
    return {
        "code": 200,
        "message": "课程查询成功",
        "data": data
    }


@router.get("/{user_id}/{course_id}/class")
async def get_course_classes(
        user_id: int,
        course_id: int,
        db: AsyncSession = Depends(get_session)
):
    """
    根据教师ID和课程ID获取班级列表
    """
    data = await get_course_classes_logic(db, user_id, course_id)
    if data is None:
        raise HTTPException(status_code=403, detail="课程不存在或您无权查看此课程的班级")
    return {
        "code": 200,
        "message": "班级列表查询成功",
        "data": data
    }


@router.get("/{user_id}/{course_id}/{class_id}/student")
async def get_class_students(
        user_id: int,
        course_id: int,
        class_id: int,
        db: AsyncSession = Depends(get_session)
):
    """
    根据 教师ID、课程ID、班级ID 获取学生名单
    """
    data = await get_class_students_logic(db, user_id, course_id, class_id)
    return {
        "code": 200,
        "message": "学生列表查询成功",
        "data": data
    }


@router.post("/{user_id}/{course_id}/{class_id}/{assignment_id}/publish")
async def publish_assignment_api(
        user_id: int,
        course_id: int,
        class_id: int,
        assignment_id: int,
        db: AsyncSession = Depends(get_session)
):
    """
    教师发布作业：执行发布逻辑并挂载准时截止的定时任务
    """
    # 1. 执行原有的发布逻辑（写入 class_assignments 表并生成学生 submission）
    result, msg = await publish_assignment_to_class(
        db=db,
        assignment_id=assignment_id,
        class_id=class_id
    )

    if not result:
        raise HTTPException(status_code=400, detail=msg)

    # --- 新增逻辑：动态添加定时任务 ---
    job_id = f"auto_close_{result.id}"

    # 使用 AsyncIOScheduler 直接挂载异步任务，避免 Event Loop 冲突
    if result.end_at > datetime.now():
        scheduler.add_job(
            async_close_assignment_logic,  # <--- 修改这里：直接传异步函数
            trigger='date',
            run_date=result.end_at,
            args=[result.id],
            id=job_id,
            replace_existing=True
        )
        print(f"定时器已挂载：作业 {result.id} 将于 {result.end_at} 自动截止")
    # ------------------------------

    # 返回给前端格式化后的数据（保持原有格式不变）
    return {
        "code": 200,
        "message": msg + " (已同步设置自动截止任务)",
        "data": {
            "id": result.id,
            "assignment_id": result.assignment_id,
            "class_id": result.class_id,
            "title": result.title,
            "max_score": result.max_score,
            "start_at": result.start_at.strftime("%Y-%m-%d %H:%M"),
            "end_at": result.end_at.strftime("%Y-%m-%d %H:%M")
        }
    }


@router.get("/{user_id}/{course_id}/{class_id}/assignment")
async def get_class_assignments(
        user_id: int,
        course_id: int,
        class_id: int,
        db: AsyncSession = Depends(get_session)
):
    """
    获取特定班级下已发布的所有作业列表
    URL: teacher/{user_id}/{course_id}/{class_id}/assignment
    """
    # 权限校验（可选）：验证该 user_id 是否有权访问该 course/class

    data = await get_class_assignments_logic(db, class_id)

    return {
        "code": 200,
        "message": "查询班级作业成功",
        "data": data
    }

@router.post("/{class_assignment_id}/end")
async def end_assignment_api(
    class_assignment_id: int,
    db: AsyncSession = Depends(get_session)
):
    """
    立即结束某个已发布的班级作业
    """
    # --- 新增逻辑：撤销还没到时间的定时任务 ---
    job_id = f"auto_close_{class_assignment_id}"
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
        print(f"已手动撤销作业 {class_assignment_id} 的定时任务")
    # ------------------------------------

    result, msg = await end_class_assignment_logic(db, class_assignment_id)

    if not result:
        raise HTTPException(status_code=404, detail=msg)

    return {
        "code": 200,
        "message": msg,
        "data": {
            "id": result.id,
            "title": result.title,
            "end_at": result.end_at.strftime("%Y-%m-%d %H:%M:%S")
        }
    }


@router.get("/{class_assignment_id}/detail_show")
async def get_teacher_class_assignment_detail(
        class_assignment_id: int,
        db: AsyncSession = Depends(get_session)
):
    """
    获取班级作业详情分析
    路径参数 class_assignment_id 对应 class_assignments 表的 id
    """
    data = await get_class_assignment_detail_logic(db, class_assignment_id)

    if data is None:
        raise HTTPException(status_code=404, detail="未找到该班级作业记录")

    return {
        "code": 200,
        "message": "查询成功",
        "data": data
    }