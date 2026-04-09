from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload
from datetime import datetime
from typing import Optional, Dict, Any, List
import logging
from collections import Counter
logger = logging.getLogger(__name__)

# 导入你的模型
from models.student_submission import StudentSubmission
from models.assignment import Assignment
from models.question import Question
from models.class_student import ClassStudent
from models.class_assignment import ClassAssignment

# 导入 Repository
from repository.question_repo import QuestionRepository
from repository.submission_repo import SubmissionRepository
from repository.class_assignment_repo import ClassAssignmentRepository
from schemas.assignment import AssignmentCreate

async def create_assignment_from_temp(db: AsyncSession, schema: AssignmentCreate):
    # 1. 自动从临时表迁移并获取新 ID 列表
    new_ids = await QuestionRepository.migrate_temp_to_formal(db)
    if not new_ids:
        return None
    new_assignment = Assignment(
        user_id=schema.user_id,
        title=schema.title,
        deadline=schema.deadline,
        question_ids=new_ids,
        q_count=len(new_ids)
    )
    db.add(new_assignment)
    await QuestionRepository.clear_temp(db)
    await db.commit()
    await db.refresh(new_assignment)
    return new_assignment

async def get_assignment_detail_with_questions(db: AsyncSession, assignment_id: int):
    result = await db.execute(select(Assignment).where(Assignment.id == assignment_id))
    assignment = result.scalar_one_or_none()
    if not assignment:
        return None
    q_ids = assignment.question_ids
    q_result = await db.execute(
        select(Question).where(Question.id.in_(q_ids))
    )
    questions = q_result.scalars().all()
    return {
        "assignment_id": assignment.id,
        "title": assignment.title,
        "deadline": assignment.deadline.strftime("%Y-%m-%d %H:%M:%S") if assignment.deadline else None,
        "q_count": assignment.q_count,
        "questions": [
            {
                "id": q.id,
                "q_type": q.q_type,
                "content": q.content,
                "options_data": q.options_data,
                "correct_answer": q.correct_answer,
                "analysis": q.analysis,
                "points": q.points
            } for q in questions
        ]
    }


async def get_student_submission_report(
        db: AsyncSession,
        class_assignment_id: int,
        student_id: int
) -> Optional[Dict[str, Any]]:
    # 1. 查询班级作业及关联的作业模板
    stmt_ca = (
        select(ClassAssignment)
        .options(joinedload(ClassAssignment.assignment))
        .where(ClassAssignment.id == class_assignment_id)
    )
    result_ca = await db.execute(stmt_ca)
    class_assignment = result_ca.scalar_one_or_none()
    if not class_assignment or not class_assignment.assignment:
        return None

    # 2. 查询学生的提交记录
    stmt_sub = select(StudentSubmission).where(
        StudentSubmission.class_assignment_id == class_assignment_id,
        StudentSubmission.student_id == student_id
    )
    result_sub = await db.execute(stmt_sub)
    submission = result_sub.scalar_one_or_none()

    # 3. 批量查询题目详情
    q_ids = class_assignment.assignment.question_ids
    questions = []
    if q_ids:
        stmt_q = select(Question).where(Question.id.in_(q_ids))
        result_q = await db.execute(stmt_q)
        questions = result_q.scalars().all()
    q_dict = {q.id: q for q in questions}

    # 4. 判断逻辑：是否已经截止？
    now = datetime.now()
    is_expired = now > class_assignment.end_at

    # 5. 构建答案映射表
    ans_detail_map = {}
    if submission and submission.answer_data:
        for item in submission.answer_data:
            qid = item.get("question_id")
            if qid:
                ans_detail_map[qid] = item

    # 6. 组装数据并应用脱敏规则
    ordered_questions = []
    for q_id in q_ids:
        q = q_dict.get(q_id)
        if q:
            sub_item = ans_detail_map.get(q_id, {})
            # 兼容字段名可能为 student_answer 或 answer 的情况
            student_answer = sub_item.get("student_answer", sub_item.get("answer", []))

            # --- 脱敏逻辑：已提交但未截止，则隐藏关键评分信息 ---
            if not is_expired and submission and submission.status == 1:
                ordered_questions.append({
                    "question_id": q.id,
                    "q_type": q.q_type,
                    "content": q.content,
                    "options_data": q.options_data,
                    "correct_data": ["已隐藏"],
                    "student_answer": student_answer,
                    "analysis": "作业截止后可查看解析",
                    "points": q.points,
                    "score": "--",
                    "ai_feedback": "作业截止后显示结果"
                })
            else:
                # 已截止 或 还没提交（答题中/未开始），显示完整信息
                ordered_questions.append({
                    "question_id": q.id,
                    "q_type": q.q_type,
                    "content": q.content,
                    "options_data": q.options_data,
                    "correct_data": q.correct_answer,
                    "student_answer": student_answer,
                    "analysis": q.analysis,
                    "points": q.points,
                    "score": sub_item.get("score", 0),
                    "ai_feedback": sub_item.get("ai_feedback", "暂无评价")
                })

    # 7. 计算并组装最终结果
    display_total_score = "--"
    display_scores = {}

    if submission:
        # 逻辑：只有在作业截止后，才计算并展示 scores 的总和
        if is_expired:
            if isinstance(submission.scores, dict):
                # 对 scores 字典中的所有分数求和
                display_total_score = sum(
                    v for v in submission.scores.values()
                    if isinstance(v, (int, float))
                )
            else:
                # 如果 scores 格式异常，退而求其次使用 total_score 字段
                display_total_score = submission.total_score

            display_scores = submission.scores
        else:
            # 未截止，总分和得分详情保持隐藏
            display_total_score = "--"
            display_scores = {}

    return {
        "class_assignment_id": class_assignment_id,
        "student_id": student_id,
        "total_score": display_total_score,
        "scores": display_scores,
        "status": submission.status if submission else 0,
        "is_manual_submit": submission.is_manual_submit if submission else 0,
        "submit_at": submission.submit_at.strftime(
            "%Y-%m-%d %H:%M:%S") if submission and submission.submit_at else None,
        "answers": ordered_questions
    }


async def publish_assignment_to_class(db: AsyncSession, assignment_id: int, class_id: int):
    # 1. 获取作业模板
    result = await db.execute(select(Assignment).where(Assignment.id == assignment_id))
    assignment = result.scalar_one_or_none()

    if not assignment:
        return None, "找不到指定的作业模板"
    if not assignment.deadline:
        return None, "原作业模板未设置截止时间，无法发布"

    try:
        # 2. 计算总分 (确保 question_ids 不为空)
        total_score = 0
        if assignment.question_ids:
            score_result = await db.execute(
                select(func.sum(Question.points)).where(Question.id.in_(assignment.question_ids))
            )
            total_score = score_result.scalar() or 0

        # 3. 创建班级作业记录
        new_class_assignment = ClassAssignment(
            assignment_id=assignment_id,
            class_id=class_id,
            title=assignment.title,
            start_at=datetime.now(),
            end_at=assignment.deadline,
            max_score=int(total_score)
        )
        db.add(new_class_assignment)

        # 关键：先 flush 以获取 new_class_assignment.id
        await db.flush()

        # 4. 获取学生名单
        student_query = await db.execute(
            select(ClassStudent.student_id).where(ClassStudent.class_id == class_id)
        )
        student_ids = student_query.scalars().all()

        msg_suffix = " (当前班级暂无学生)"
        if student_ids:
            # 5. 构造提交记录 (直接用 db.add_all 往往比 Repository 更可靠)
            submissions = [
                StudentSubmission(
                    class_assignment_id=new_class_assignment.id,
                    student_id=sid,
                    submit_at=None,
                    total_score=0,
                    status=0,
                    is_manual_submit=0,
                    answer_data=[],
                    scores={},  # 建议给 json 字段一个初始空字典，防止报错
                    ai_feedback=None
                )
                for sid in student_ids
            ]
            db.add_all(submissions)
            msg_suffix = f" (已自动为 {len(student_ids)} 名学生生成答题记录)"

        # 6. 统一提交
        await db.commit()
        # 刷新对象以便返回给前端
        await db.refresh(new_class_assignment)
        return new_class_assignment, "发布成功" + msg_suffix

    except Exception as e:
        await db.rollback()
        # 打印详细错误到控制台，这是定位问题的终极手段
        logger.error(f"Publish failed: {str(e)}", exc_info=True)
        return None, f"发布失败: {str(e)}"

async def get_class_assignments_logic(db: AsyncSession, class_id: int):
    assignments = await ClassAssignmentRepository.get_assignments_by_class_id(db, class_id)
    if not assignments:
        return []
    return [
        {
            "id": a.id,
            "assignment_id": a.assignment_id,
            "title": a.title,
            "max_score": a.max_score,
            "start_at": a.start_at.strftime("%Y-%m-%d %H:%M"),
            "end_at": a.end_at.strftime("%Y-%m-%d %H:%M")
        }
        for a in assignments
    ]


async def end_class_assignment_logic(db: AsyncSession, class_assignment_id: int):
    # 1. 查找并更新 ClassAssignment 的逻辑 (假设你已有这部分代码)
    assignment = await db.get(ClassAssignment, class_assignment_id)
    if not assignment:
        return None, "作业不存在"

    # 更新截止时间为当前时间
    assignment.end_at = datetime.now()

    try:
        # 2. 调用 Repository 更新 student_submissions 表的状态为 1
        await SubmissionRepository.update_status_by_assignment_id(
            db,
            class_assignment_id,
            new_status=1
        )

        # 3. 提交事务
        await db.commit()
        await db.refresh(assignment)

        return assignment, "作业已成功结束并更新学生提交状态"

    except Exception as e:
        await db.rollback()
        return None, f"操作失败: {str(e)}"


async def get_class_assignment_detail_logic(db: AsyncSession, ca_id: int):
    # 1. 查找 class_assignments 表中 id = ca_id 的记录
    ca = await ClassAssignmentRepository.get_by_id(db, ca_id)
    if not ca:
        return None

    # 2. 查找 student_submissions 表中 class_assignment_id = ca_id 的所有记录
    submissions = await SubmissionRepository.get_submissions_by_class_assignment_id(db, ca_id)

    # --- 基础统计 ---
    total_student = len(submissions)
    # 统计 is_manual_submit = 1 的记录数 (对应你要求的 submit_student)
    submit_student = sum(1 for s in submissions if s.is_manual_submit == 1)

    # 统计平均值
    submitted_scores = [s.total_score for s in submissions if s.is_manual_submit == 1]
    average_score = sum(submitted_scores) / submit_student if submit_student > 0 else 0

    # --- 知识点分布汇总 ---
    # 逻辑：遍历每个记录的 analysis_report['knowledge']，将相同 key 的 count 相加
    kn_counter = Counter()
    for s in submissions:
        if s.analysis_report and isinstance(s.analysis_report, dict):
            # 1. 对应你 JSON 中的键名 "knowledge_distribution"
            kn_list = s.analysis_report.get("knowledge_distribution", [])

            # 2. 因为是列表，需要遍历列表
            if isinstance(kn_list, list):
                for item in kn_list:
                    # 3. 提取 key 和 counts (注意是 counts)
                    name = item.get("key")
                    count = item.get("counts", 0)
                    if name:
                        # 确保 count 是数字
                        kn_counter[name] += (count if isinstance(count, (int, float)) else 0)

    knowledge_distribution = [
        {"key": k, "count": v} for k, v in kn_counter.items()
    ]

    # --- 学生排行/详情列表 ---
    rank_data = []
    for s in submissions:
        rank_data.append({
            "name": s.student.name if s.student else f"未知学生({s.student_id})",
            "submit_at": s.submit_at.strftime("%Y-%m-%d %H:%M:%S") if s.submit_at else None,
            "is_manual": s.is_manual_submit,
            "total_score": s.total_score if s.is_manual_submit == 1 else None  # 配合前端显示 '--'
        })

    # --- 核心修改：多级排序逻辑 ---
    # 逻辑说明：
    # 1. (x['is_manual'] == 0) : 已提交(1)的比较结果为 False(0)，未提交(0)为 True(1)。升序排，则 0 在前，1 在后。
    # 2. -(x['total_score'] or 0) : 取负号实现降序。分数越高，负值越小，排在越前面。
    # 3. x['submit_at'] or '9999' : 如果分数相同，按提交时间升序（先交的在前面）。
    rank_data.sort(key=lambda x: (
        x['is_manual'] == 0,  # 第一优先级：已提交状态 (False=0 < True=1)
        -(x['total_score'] or 0),  # 第二优先级：分数降序
        x['submit_at'] or '9999'  # 第三优先级：提交时间升序
    ))

    # 3. 按照要求的格式返回
    return {
        "total_student": total_student,
        "submit_student": submit_student,
        "max_score": ca.max_score,
        "average_score": round(average_score, 2),
        "create_at": ca.start_at.strftime("%Y-%m-%d %H:%M:%S") if ca.start_at else None,
        "end_at": ca.end_at.strftime("%Y-%m-%d %H:%M:%S") if ca.end_at else None,
        "knowledge_distribution": knowledge_distribution,
        "rank": rank_data
    }