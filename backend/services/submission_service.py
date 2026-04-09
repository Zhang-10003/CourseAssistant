import json
import asyncio
from datetime import datetime
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from models.question import Question
from models.student_submission import StudentSubmission
import json
import logging

# 初始化日志，方便调试
logger = logging.getLogger(__name__)

async def submit_student_answers_logic(db: AsyncSession, class_assignment_id: int, student_id: int, payload: dict,
                                       llm_model):
    """
    核心业务逻辑：以服务器当前时间作为提交时间，保存答案并异步批改
    """
    answers_from_front = payload.get("answers", [])

    # 1. 获取服务器当前时间
    # 建议使用 datetime.now() 记录到数据库
    current_submit_time = datetime.now()

    # 2. 清洗数据
    clean_answers = []
    for a in answers_from_front:
        qid = a.get("question_id")
        # 过滤掉无效或 fallback 的 ID
        if not qid or (isinstance(qid, str) and "fallback" in qid):
            continue
        clean_answers.append({
            "question_id": int(qid),
            "q_type": a.get("q_type"),
            "student_answer": a.get("student_answer")
        })

    # 3. 立即存入数据库
    try:
        stmt = (
            update(StudentSubmission)
            .where(
                StudentSubmission.class_assignment_id == class_assignment_id,
                StudentSubmission.student_id == int(student_id)
            )
            .values(
                submit_at=current_submit_time,  # 使用服务器当前时间
                answer_data=clean_answers,
                status=0,
                is_manual_submit=1
            )
        )
        await db.execute(stmt)
        await db.commit()
    except Exception as e:
        await db.rollback()
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"保存失败: {str(e)}")

    # 4. 异步执行耗时任务
    asyncio.create_task(run_background_grading(db, class_assignment_id, int(student_id), clean_answers, llm_model))
    asyncio.create_task(run_background_analysis(db, class_assignment_id, int(student_id), clean_answers, llm_model))

    return {
        "class_assignment_id": class_assignment_id,
        "submit_at": current_submit_time.strftime("%Y-%m-%d %H:%M:%S")  # 返回给前端确认
    }



async def run_background_grading(db: AsyncSession, ca_id: int, s_id: int, answers: list, model):
    """后台任务：获取题目详情并调用你原有的 AI 逻辑"""
    try:
        q_ids = [a["question_id"] for a in answers]
        q_result = await db.execute(select(Question).where(Question.id.in_(q_ids)))
        q_map = {q.id: q for q in q_result.scalars().all()}

        full_data_to_grade = []
        for ans in answers:
            q = q_map.get(ans["question_id"])
            if q:
                full_data_to_grade.append({
                    "question_id": q.id,
                    "q_type": q.q_type,
                    "content": q.content,
                    "options_data": q.options_data,
                    "correct_data": q.correct_answer,  # 匹配你原有的键名
                    "analysis": q.analysis,
                    "full_points": q.points,
                    "student_answer": ans.get("student_answer")
                })

        # 调用你原有的批改函数（提示词在里面）
        graded_answers = await _invoke_llm_grading(full_data_to_grade, model)

        if graded_answers:
            total_score = sum(int(item.get("score", 0)) for item in graded_answers)
            scores_list = [int(item.get("score", 0)) for item in graded_answers]

            stmt = (
                update(StudentSubmission)
                .where(StudentSubmission.class_assignment_id == ca_id, StudentSubmission.student_id == s_id)
                .values(answer_data=graded_answers, scores=scores_list, total_score=total_score)
            )
            await db.execute(stmt)
            await db.commit()
    except Exception as e:
        print(f"后台异步批改失败: {e}")


async def run_background_analysis(db: AsyncSession, ca_id: int, s_id: int, answers: list, model):
    """后台任务：生成知识点分析报告并存入数据库"""
    try:
        # 1. 准备数据
        q_ids = [a["question_id"] for a in answers]
        q_result = await db.execute(select(Question).where(Question.id.in_(q_ids)))
        q_map = {q.id: q for q in q_result.scalars().all()}

        full_data_to_analyze = []
        for ans in answers:
            q = q_map.get(ans["question_id"])
            if q:
                full_data_to_analyze.append({
                    "question_id": q.id,
                    "content": q.content,
                    "correct_data": q.correct_answer,
                    "analysis": q.analysis,
                    "student_answer": ans.get("student_answer")
                })

        # 2. 获取 AI 分析结果（此时 report_obj 是一个 dict）
        report_obj = await _invoke_llm_analysis(full_data_to_analyze, model)

        # 3. 存储到数据库
        if report_obj:
            stmt = (
                update(StudentSubmission)
                .where(StudentSubmission.class_assignment_id == ca_id, StudentSubmission.student_id == s_id)
                .values(analysis_report=report_obj) # 关键：传入 dict 对象，避免数据库出现转义斜杠
            )
            await db.execute(stmt)
            await db.commit()
            print(f"成功为学生 {s_id} 存入深度分析报告")

    except Exception as e:
        # 发生错误回滚
        await db.rollback()
        print(f"后台知识点分析失败: {e}")


async def _invoke_llm_grading(tasks: list, model):
    """
    批改函数：返回解析后的题目列表对象
    """
    prompt = f"""
    Role: 你是一位专业的大学老师，擅长客观、严谨地批改简答题。
    Task: 请对【待批改数据包】进行打分并给出详细反馈。

    【待批改数据包】:
    {json.dumps(tasks, ensure_ascii=False)}

    【批改指令】:
    1. **客观题(q_type 0或1)**: 对比 student_answer 和 correct_data。完全一致给 full_points，否则给 0。
    2. **简答题(q_type 2)**: 
       - 提取要点：对比标准答案中的得分点。
       - 对比分析：标注学生答案是否涵盖要点。
       - 计算分数：根据满分(full_points)按比例给出得分。
    3. **输出要求**: **必须原样保留**输入的所有字段，并为每一项填充：
       - "score": 最终得分 (int)
       - "ai_feedback": 具体的批改反馈建议 (string)

    必须仅返回 JSON 数组，禁止包含 ```json 标识。
    """
    response = await model.ainvoke(prompt)
    content = response.content.strip()

    # 清洗并解析
    if "[" in content:
        content = content[content.find("["):content.rfind("]") + 1]

    try:
        return json.loads(content)  # 返回 list 对象
    except:
        return None


async def _invoke_llm_analysis(tasks: list, model):
    """
    专门用于知识点提取和学生薄弱环节分析的 AI 调用函数。
    返回：解析后的 JSON 对象 (dict)
    """
    payload_json = json.dumps(tasks, indent=4, ensure_ascii=False)

    print("\n" + ">" * 20 + " 发送给 AI 的分析数据包 " + "<" * 20)
    print(payload_json)
    print(">" * 60 + "\n")

    prompt = f"""
    # Role
    你是一名资深的计算机科学教育专家和数据分析师。你擅长根据题目内容精准提取知识点（Knowledge Points），并能从结构化的作业数据中分析学生的薄弱环节。

    # Task
    分析提供的学生作业数据（JSON格式），识别核心知识点，判定答题正误，并生成结构化的诊断分析报告。

    # Data Context (JSON)
    {json.dumps(tasks, ensure_ascii=False)}

    # Instructions
    1. **知识点提取**：基于 `content`（题面）和 `analysis`（解析）提取精炼、专业的计算机科学术语。
    2. **正误判定**：对比 `student_answer` 与 `correct_data`。若两者不匹配，则判定为“错误”。
    3. **统计分布**：仅针对“错误”题目涉及的知识点进行频次统计。
    4. **排序要求**：`knowledge_distribution` 中的项必须按 `counts` 频次从高到低（降序）排列。
    5. **深度诊断**：在 `analysis_summary` 中提供不少于 200 字的专业分析，涵盖错题成因、认知误区及后续提升建议。

    # Constraints
    - 知识点提取需具备学术严谨性，严禁口语化。
    - **输出规范**：必须仅返回一个合法的 JSON 对象。严禁包含 ```json 代码块标识、前导说明或后置总结。
    - **鲁棒性**：若数据字段缺失，请基于专业背景进行逻辑推断。

    # Output Schema
    {{
        "analysis_summary": "此处填写资深的薄弱环节分析与针对性教学建议",
        "knowledge_distribution": [
            {{ "key": "核心知识点A", "counts": 3 }},
            {{ "key": "核心知识点B", "counts": 1 }}
        ]
    }}
    """

    try:
        response = await model.ainvoke(prompt)
        content = response.content.strip()

        # 强力清洗逻辑：只截取第一个 '{' 到最后一个 '}' 之间的内容，彻底剔除修饰文字
        if "{" in content:
            content = content[content.find("{"):content.rfind("}") + 1]

        # 将字符串转化为 Python 对象，这一步会自动处理掉 \n 和 \" 转义
        analysis_obj = json.loads(content)

        print("\n" + "=" * 20 + " AI 结构化分析结果 (已去转义) " + "=" * 20)
        # 使用 indent 打印是为了在控制台好看，存入数据库时会是纯净的 JSON
        print(json.dumps(analysis_obj, indent=4, ensure_ascii=False))
        print("=" * 60 + "\n")

        return analysis_obj

    except Exception as e:
        logger.error(f"AI 分析任务解析失败: {str(e)}")
        return None

