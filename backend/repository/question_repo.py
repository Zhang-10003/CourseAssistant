from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from models.question import Question
from models.temp_question import TempQuestion


class QuestionRepository:
    @staticmethod
    async def save_to_temp(db: AsyncSession, questions_data: list):
        for q in questions_data:
            is_essay = q.get('q_type') == 2
            # 强制根据题型重新计算分值，忽略 AI 返回的 points
            calculated_points = 10 if is_essay else 5

            db_q = TempQuestion(
                q_type=q.get('q_type'),
                content=q.get('content'),
                options_data=None if is_essay else q.get('options_data'),
                correct_answer=q.get('correct_answer'),
                analysis=q.get('analysis'),
                points=calculated_points  # 使用强制计算的值
            )
            db.add(db_q)

    @staticmethod
    async def migrate_temp_to_formal(db: AsyncSession):
        """将临时表所有数据搬运到正式表，并返回正式表的新ID列表"""
        # 1. 获取临时表所有记录
        result = await db.execute(select(TempQuestion))
        temp_items = result.scalars().all()

        if not temp_items:
            return []

        new_ids = []
        for t in temp_items:
            # 2. 转换为正式表对象
            formal_q = Question(
                q_type=t.q_type,
                content=t.content,
                options_data=t.options_data,
                correct_answer=t.correct_answer,
                analysis=t.analysis,
                points=t.points
            )
            db.add(formal_q)
            await db.flush()  # 核心：立即获取数据库生成的自增 ID
            new_ids.append(formal_q.id)

        return new_ids

    @staticmethod
    async def clear_temp(db: AsyncSession):
        """清空临时表"""
        await db.execute(delete(TempQuestion))