from sqlalchemy import Integer, String, DateTime, ForeignKey, JSON, SmallInteger, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional, Any, List,Dict
from models import Base


class StudentSubmission(Base):
    """
    学生作业提交记录表
    关联 ClassAssignment (班级发布的作业实例) 和 Student
    """
    __tablename__ = 'student_submissions'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    class_assignment_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("class_assignments.id", ondelete="CASCADE"),
        nullable=False
    )

    student_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("students.student_id", ondelete="CASCADE"),
        nullable=False
    )

    submit_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=None)

    # --- 修改部分：将 score 改为 scores 数组形式 ---
    # 格式建议：List[int]，例如 [5, 0, 10] 对应 answer_data 中每一题的得分
    scores: Mapped[Optional[List[int]]] = mapped_column(JSON, default=[], nullable=False)

    # 如果你依然想保留一个“总分”字段方便查询排名的，可以增加一个总分字段：
    total_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    # ------------------------------------------

    ai_feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    analysis_report: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    # answer_data: 学生答案。
    # 格式：[{"question_id": 1, "q_type": 0, "student_answer": [0]}, ...]
    answer_data: Mapped[Optional[List[Any]]] = mapped_column(JSON, nullable=True)

    status: Mapped[int] = mapped_column(SmallInteger, default=0, nullable=False)

    is_manual_submit: Mapped[int] = mapped_column(SmallInteger, default=0, nullable=False)
    student: Mapped["Student"] = relationship("Student", foreign_keys=[student_id])
    def __repr__(self) -> str:
        return (f"<StudentSubmission(id={self.id}, student={self.student_id}, "
                f"class_assignment={self.class_assignment_id}, scores={self.scores})>")