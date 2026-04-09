from datetime import timedelta, datetime
from sqlalchemy import select,func
from models import AsyncSession
from models.class_student import ClassStudent
from models.course_class import CourseClass
from models.emailcode import EmailCode
from models.student import Student
from models.teacher import Teacher
from models.user import User

"""
    用户相关的数据库操作
"""


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    # 新增：根据 user_id 返回 User 对象 (修复 AttributeError)
    async def get_by_id(self, user_id: int) -> User | None:
        # 注意：这里不用再开 async with self.session.begin()，
        # 因为 Depends(get_session) 通常已经管理了事务周期
        stmt = select(User).where(User.user_id == user_id)
        user = await self.session.scalar(stmt)
        return user

    # 根据用户名返回 User
    async def get_by_username(self, username: str) -> User | None:
        stmt = select(User).where(User.username == username)
        user = await self.session.scalar(stmt)
        return user

    async def get_real_name(self, user: User) -> str:
        """
        核心逻辑：根据 user 对象中的类型去不同表查姓名
        0: 管理员, 1: 教师, 2: 学生
        """
        if user.user_type == 2:
            stmt = select(Student.name).where(Student.student_id == user.user_id)
        elif user.user_type == 1:
            stmt = select(Teacher.name).where(Teacher.teacher_id == user.user_id)
        elif user.user_type == 0:
            return f"管理员({user.username})"
        else:
            return "未知身份"

        result = await self.session.execute(stmt)
        name = result.scalar()
        return name or user.username

    # 之前缩进错误的方法，挪回 UserRepository 下
    async def get_teacher_profile(self, user_id: int) -> Teacher | None:
        stmt = select(Teacher).where(Teacher.teacher_id == user_id)
        teacher = await self.session.scalar(stmt)
        return teacher

    # @staticmethod
    # async def get_student_class_info(db: AsyncSession, user_id: int):
    #     # 1. 获取该学生加入的所有 class_id (使用 scalars().all())
    #     stmt = select(ClassStudent.class_id).where(ClassStudent.student_id == user_id)
    #     result = await db.execute(stmt)
    #     class_ids = result.scalars().all()
    #
    #     if not class_ids:
    #         return []  # 如果没加入任何班级，返回空列表
    #
    #     # 2. 准备存储所有班级信息的列表
    #     classes_info = []
    #
    #     # 3. 循环获取每个班级的详细信息
    #     for cid in class_ids:
    #         # 获取班级名称
    #         name_stmt = select(CourseClass.class_name).where(CourseClass.class_id == cid)
    #         name_result = await db.execute(name_stmt)
    #         class_name = name_result.scalar_one_or_none()
    #
    #         # 统计该班级总人数
    #         count_stmt = select(func.count(ClassStudent.student_id)).where(ClassStudent.class_id == cid)
    #         count_result = await db.execute(count_stmt)
    #         total_students = count_result.scalar()
    #
    #         # 将该班级信息加入列表
    #         classes_info.append({
    #             "class_name": class_name,
    #             "total_students": total_students
    #         })
    #
    #     return classes_info  # 返回包含多个班级的列表
    @staticmethod
    async def get_student_class_info(db: AsyncSession, user_id: int):
        # 1. 构造聚合查询：连接 ClassStudent 和 CourseClass
        # 统计每个班级的总人数，并过滤出当前学生所在的班级

        # 子查询：先统计所有班级的人数
        subq = (
            select(
                ClassStudent.class_id,
                func.count(ClassStudent.student_id).label("total_students")
            )
            .group_by(ClassStudent.class_id)
            .subquery()
        )

        # 主查询：获取学生加入的班级详情
        stmt = (
            select(
                CourseClass.class_id,
                CourseClass.class_name,
                subq.c.total_students
            )
            .join(subq, CourseClass.class_id == subq.c.class_id)
            .join(ClassStudent, CourseClass.class_id == ClassStudent.class_id)
            .where(ClassStudent.student_id == user_id)
        )

        result = await db.execute(stmt)
        # 使用 mappings() 直接获取字典格式的结果
        rows = result.mappings().all()

        # 2. 转换为列表返回
        return [
            {
                "class_id": row["class_id"],
                "class_name": row["class_name"],
                "total_students": row["total_students"]
            }
            for row in rows
        ]

"""
    邮箱验证码相关的数据库操作
"""


class EmailCodeRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, email: str, code: str) -> EmailCode:
        async with self.session.begin():
            email_code = EmailCode(email=email, code=code)
            self.session.add(email_code)
            return email_code

    async def check_email_code(self, email: str, code: str) -> bool:
        # 这里的 begin() 视你的 get_session 实现而定，
        # 如果 get_session 已经 yield session 了，这里通常不需要 begin
        stmt = select(EmailCode).where(EmailCode.email == email, EmailCode.code == code)
        email_code = await self.session.scalar(stmt)

        if email_code is None:
            return False

        # 修复：datetime.now 是函数，需要加括号 ()
        if (datetime.now() - email_code.create_time) > timedelta(minutes=5):
            return False
        return True