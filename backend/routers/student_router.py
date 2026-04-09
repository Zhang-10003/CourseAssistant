from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from dependencies import get_session
from services.assignment_service import get_class_assignments_logic, get_assignment_detail_with_questions, \
    get_student_submission_report
from services.submission_service import submit_student_answers_logic
from services.user_service import get_student_class_logic
from schemas.user import StudentClassResponse
from typing import List  # 1. 必须导入 List
from schemas.assignment import ClassAssignmentListItem
from services.ai_service import model as llm_model

router = APIRouter(prefix="/student", tags=["student"])


# 2. 将 StudentClassResponse 改为 List[StudentClassResponse]
@router.get("/{user_id}/class", response_model=List[StudentClassResponse])
async def get_student_class(user_id: int, db: AsyncSession = Depends(get_session)):
    result = await get_student_class_logic(db, user_id)

    # 注意：现在 result 是列表，没找到数据会返回空列表 []
    # 如果你希望在没有班级时报 404，可以这样判断：
    if not result:
        raise HTTPException(status_code=404, detail="未找到该学生的班级信息")

    return result


@router.get("/{class_id}/assignment", response_model=List[ClassAssignmentListItem])
async def get_student_assignments(
        class_id: int,
        db: AsyncSession = Depends(get_session)
):
    """
    学生端接口：获取指定班级的所有作业记录
    - class_id: 路径参数，班级唯一标识
    """
    # 调用 Service 层获取数据
    result = await get_class_assignments_logic(db, class_id)

    # 直接返回列表，FastAPI 会根据 response_model 自动序列化
    return result


@router.get("/{assignment_id}/detail")
async def get_assignment_detail(
    assignment_id: int,
    student_id: int,  # 确保这里接收了学生ID
    db: AsyncSession = Depends(get_session)
):
    data = await get_student_submission_report(db, assignment_id, student_id)

    if not data:
        raise HTTPException(status_code=404, detail="未找到该作业详情或提交记录")

    return {"code": 200, "message": "查询成功", "data": data}


@router.post("/{class_assignment_id}/{student_id}/submit")
async def student_submit_assignment(
        class_assignment_id: int,
        student_id: int,
        payload: dict,
        db: AsyncSession = Depends(get_session)
):
    """
    学生提交并获取实时 AI 批改详情
    """
    try:
        # 调用逻辑层获取“全量数据包”
        result_data = await submit_student_answers_logic(
            db, class_assignment_id, student_id, payload, llm_model
        )

        # 封装成你需要的 code/message/data 格式
        return {
            "code": 200,
            "message": "提交并批改成功",
            "data": result_data
        }
    except Exception as e:
        # 打印详细报错到控制台，方便排查 KeyError
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))