from sqlalchemy.ext.asyncio import AsyncSession
from repository.user_repo import UserRepository

async def get_student_class_logic(db: AsyncSession, user_id: int):
    data = await UserRepository.get_student_class_info(db, user_id)
    if not data:
        return None
    return data