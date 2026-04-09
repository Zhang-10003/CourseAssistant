from sqlalchemy import select, func, desc  # 1. 导入 desc
from sqlalchemy.ext.asyncio import AsyncSession
from models.class_assignment import ClassAssignment
from models.question import Question

class ClassAssignmentRepository:
    @staticmethod
    async def get_total_points(db: AsyncSession, question_ids: list[int]) -> int:
        """根据题目ID列表计算总分"""
        if not question_ids:
            return 0
        stmt = select(func.sum(Question.points)).where(Question.id.in_(question_ids))
        result = await db.execute(stmt)
        return result.scalar() or 0

    @staticmethod
    async def create_class_assignment(db: AsyncSession, data: ClassAssignment):
        """保存班级作业发布记录"""
        db.add(data)
        await db.flush() # 先 flush 获取 ID，由 service 统一 commit
        return data

    @staticmethod
    async def get_assignments_by_class_id(db: AsyncSession, class_id: int):
        """
        根据班级 ID 查询该班级所有已发布的作业
        并按照截止时间降序排列（最晚的在最前面）
        """
        # 使用 .order_by(ClassAssignment.end_at.desc()) 实现排序
        stmt = (
            select(ClassAssignment)
            .where(ClassAssignment.class_id == class_id)
            .order_by(desc(ClassAssignment.end_at))
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_by_id(db: AsyncSession, assignment_id: int) -> ClassAssignment:
        """根据 ID 查找班级作业记录"""
        stmt = select(ClassAssignment).where(ClassAssignment.id == assignment_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def update_end_time_to_now(db: AsyncSession, assignment_id: int):
        """将截止时间更新为当前时间"""
        assignment = await ClassAssignmentRepository.get_by_id(db, assignment_id)
        if assignment:
            assignment.end_at = datetime.now()
            await db.flush()  # 提交到数据库会话
        return assignment