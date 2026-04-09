import asyncio
from datetime import datetime
from sqlalchemy import update
from models import AsyncSessionFactory
from models.student_submission import StudentSubmission

async def async_close_assignment_logic(ca_id: int):
    """
    具体的数据库操作：由调度器直接调用的异步任务
    """
    print(f"--- [任务执行] 开始自动截止班级作业 ID: {ca_id} ---")

    async with AsyncSessionFactory() as db:
        try:
            # 1. 执行批量更新
            stmt = (
                update(StudentSubmission)
                .where(StudentSubmission.class_assignment_id == ca_id)
                .where(StudentSubmission.status == 0)  # 只处理未提交的学生
                .values(status=1)
            )

            result = await db.execute(stmt)
            affected_rows = result.rowcount

            # 2. 显式提交事务
            await db.commit()

            print(f"--- [任务结果] 作业 {ca_id} 自动截止成功！更新了 {affected_rows} 条学生记录 ---")

        except Exception as e:
            await db.rollback()
            print(f"--- [任务失败] 自动关闭异常: {str(e)} ---")