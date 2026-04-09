from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship  # 1. 导入 relationship
from datetime import datetime
from typing import Optional
from models import Base


class ClassAssignment(Base):
    __tablename__ = 'class_assignments'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    assignment_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("assignments.id", ondelete="CASCADE"),
        nullable=False
    )

    # 2. 添加这一行！建立与 Assignment 模型的关系
    # 注意：确保你的 "Assignment" 类名拼写正确
    assignment: Mapped["Assignment"] = relationship("Assignment")

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    class_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("course_classes.class_id", ondelete="CASCADE"),
        nullable=False
    )
    start_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    max_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    def __repr__(self) -> str:
        return f"<ClassAssignment(id={self.id}, title='{self.title}')>"