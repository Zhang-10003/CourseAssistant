from sqlalchemy.ext.asyncio import AsyncSession
from models.assignment import Assignment
from sqlalchemy import select
class AssignmentRepository:
    @staticmethod
    async def create_assignment(db: AsyncSession, title: str, question_ids: list, deadline=None):
        new_assignment = Assignment(
            title=title,
            deadline=deadline,
            question_ids=question_ids
        )
        db.add(new_assignment)
        return new_assignment

    @staticmethod
    async def get_assignments_by_user_id(db: AsyncSession, user_id: int):
        """
        根据 user_id 返回该用户的所有作业记录
        """
        result = await db.execute(
            select(Assignment).where(Assignment.user_id == user_id)
        )
        return result.scalars().all()