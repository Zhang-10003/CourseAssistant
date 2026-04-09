from sqlalchemy import Integer, Text, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from models import Base


class Question(Base):
    __tablename__ = 'questions'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    q_type: Mapped[int] = mapped_column(Integer, nullable=False)  # 0:单选, 1:多选, 2:简答
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # options_data 设为 JSON，兼容数组或空
    options_data: Mapped[list] = mapped_column(JSON, nullable=True)

    # correct_answer 设为 JSON，兼容索引列表 [0] 或 文本列表 ["答案"]
    correct_answer: Mapped[list] = mapped_column(JSON, nullable=False)

    analysis: Mapped[str] = mapped_column(Text, nullable=True)
    points: Mapped[int] = mapped_column(Integer, default=5)