from sqlalchemy import Integer, String, Text, JSON, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional, List
from datetime import datetime

from models import Base


class Assignment(Base):
    __tablename__ = 'assignments'

    # id: int, 自增, 主键
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # 用户ID: 外键关联到 users 表的 id 字段
    # 注意: 这里的 'users.id' 需根据你 User 类的 __tablename__ 和主键名调整
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.user_id"), nullable=False)

    # 作业名称: str, 非空
    title: Mapped[str] = mapped_column(String(255), nullable=False)

    # 创建时间: datetime, 非空, 默认为当前服务器时间
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    q_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # 截止时间: datetime, 可以为空
    deadline: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # 题目列表: 存储为 JSON 数组
    question_ids: Mapped[List[int]] = mapped_column(JSON, nullable=False, default=list)