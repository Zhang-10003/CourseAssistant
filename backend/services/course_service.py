# services/course_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from repository.course_repo import CourseRepository


async def get_course_classes_logic(db: AsyncSession, user_id: int, course_id: int):
    # ... 前面的查询逻辑保持不变 ...
    classes = await CourseRepository.get_classes_by_course_id(db, user_id, course_id)

    if classes is None:
        return None

    data = [
        {
            "class_id": cls.class_id,
            "class_name": cls.class_name,
            "course_id": cls.course_id
        }
        for cls in classes
    ]
    return data


async def get_class_students_logic(db: AsyncSession, user_id: int, course_id: int, class_id: int):
    """
    业务逻辑：获取特定班级的学生列表
    """
    students = await CourseRepository.get_students_by_class_id(db, user_id, course_id, class_id)

    if not students:
        return []
    data = [
        {
            "student_no": f"{s.student_no:05d}",  # 格式化为5位学号
            "name": s.name,
            "email": s.email
        }
        for s in students
    ]
    return data