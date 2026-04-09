from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from models import Base

class CourseClass(Base):
    __tablename__ = 'course_classes'

    class_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    class_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    # 3. course_id: FK (关联 course 表的 course_id)
    # 实现“一门课程对应多个班级”的一对多关系
    course_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("courses.course_id"),
        nullable=False
    )
    def __repr__(self) -> str:
        return f"<CourseClass(id={self.class_id}, name='{self.class_name}', course_id={self.course_id})>"