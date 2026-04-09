from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.class_student import ClassStudent
from models.course import Course  # 确保路径指向你定义的 Course 模型
from models.course_class import CourseClass
from models.student import Student


class CourseRepository:
    @staticmethod
    async def get_courses_by_teacher_id(db: AsyncSession, teacher_id: int):
        """
        根据教师 ID 查询课程列表
        """
        result = await db.execute(
            select(Course).where(Course.teacher_id == teacher_id)
        )
        return result.scalars().all()

    @staticmethod
    async def get_classes_by_course_id(db: AsyncSession, teacher_id: int, course_id: int):
        """
        1. 验证该课程是否属于该教师
        2. 返回该课程下的所有班级记录
        """
        # 首先校验权限：在 Course 表中找 teacher_id == user_id 且 course_id 匹配的记录
        check_query = await db.execute(
            select(Course).where(Course.teacher_id == teacher_id, Course.course_id == course_id)
        )
        course = check_query.scalar_one_or_none()
        if not course:
            return None  # 或者抛出异常，表示无权访问或课程不存在
        # 查找 course_classes 表中 course_id 匹配的所有记录
        class_query = await db.execute(
            select(CourseClass).where(CourseClass.course_id == course_id)
        )
        return class_query.scalars().all()

    @staticmethod
    async def get_students_by_class_id(db: AsyncSession, teacher_id: int, course_id: int, class_id: int):
        """
        通过 teacher_id -> course_id -> class_id 校验权限
        并最终返回该班级下的所有学生信息
        """
        # 构造查询：连接 Course, CourseClass, ClassStudent 和 Student 表
        query = (
            select(Student.student_no, Student.name, Student.email)
            .join(ClassStudent, Student.student_id == ClassStudent.student_id)
            .join(CourseClass, ClassStudent.class_id == CourseClass.class_id)
            .join(Course, CourseClass.course_id == Course.course_id)
            .where(
                Course.teacher_id == teacher_id,
                Course.course_id == course_id,
                CourseClass.class_id == class_id
            )
        )

        result = await db.execute(query)
        # 返回元组列表 [(student_no, name, email), ...]
        return result.all()