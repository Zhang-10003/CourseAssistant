from sqlalchemy import Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from models import Base

class ClassStudent(Base):
    __tablename__ = 'class_students'

    class_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("course_classes.class_id", ondelete="CASCADE"),
        primary_key=True
    )
    student_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("students.student_id", ondelete="CASCADE"),
        primary_key=True
    )
    course_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("courses.course_id", ondelete="CASCADE"),
        nullable=False
    )
    # 强制执行“学生在同一门课只能在一个班”的业务逻辑
    __table_args__ = (
        UniqueConstraint('student_id', 'course_id', name='uq_student_course_limit'),
    )
    def __repr__(self) -> str:
        return f"<ClassStudent(class_id={self.class_id}, student_id={self.student_id}, course_id={self.course_id})>"