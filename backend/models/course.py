from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from models import Base


class Course(Base):
    __tablename__ = 'courses'

    # course_id: PK
    course_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # course_name: 课程名称 (如：计算机网络、操作系统)
    course_name: Mapped[str] = mapped_column(String(255), nullable=False)

    # teacher_id: FK (关联 teacher.teacher_id)
    teacher_id: Mapped[int] = mapped_column(Integer, ForeignKey('teachers.teacher_id'), nullable=False)