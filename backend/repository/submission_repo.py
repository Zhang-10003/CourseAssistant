from sqlalchemy.ext.asyncio import AsyncSession
from models.student_submission import StudentSubmission
from sqlalchemy import update, select
from sqlalchemy.orm import joinedload
class SubmissionRepository:
    @staticmethod
    async def create_submissions_batch(db: AsyncSession, submissions: list[StudentSubmission]):
        """
        批量插入学生提交记录
        """
        db.add_all(submissions)
        # 注意：此处不 commit，由 Service 层统一管理事务
        return True

    @staticmethod
    async def update_status_by_assignment_id(db: AsyncSession, class_assignment_id: int, new_status: int):
        """
        根据作业ID批量更新学生提交记录的状态
        """
        stmt = (
            update(StudentSubmission)
            .where(StudentSubmission.class_assignment_id == class_assignment_id)
            .values(status=new_status)
        )
        await db.execute(stmt)
        return True

    @staticmethod
    async def get_submissions_by_class_assignment_id(db: AsyncSession, ca_id: int):
        """
        通过 class_assignment_id 查询所有学生提交记录，并关联学生基本信息
        """
        stmt = (
            select(StudentSubmission)
            .options(joinedload(StudentSubmission.student))  # 关联 Student 模型
            .where(StudentSubmission.class_assignment_id == ca_id)
        )
        result = await db.execute(stmt)
        return result.scalars().all()