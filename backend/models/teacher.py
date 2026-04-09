from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from models import Base

class Teacher(Base):
    __tablename__ = 'teachers'

    # 1. teacher_id: 既是主键，又是外键，指向 user 表的 id
    teacher_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user.user_id"),
        primary_key=True,
        nullable=False
    )
    # 2. teacher_no: 唯一且自增
    teacher_no: Mapped[int] = mapped_column(
        Integer,
        unique=True,
        autoincrement=True,
        nullable=False
    )

    # 3. name & email: 非空
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    def __repr__(self) -> str:
        # 在控制台打印时自动展示 4 位格式化后的编号
        return f"<Teacher(id={self.teacher_id}, no={self.teacher_no:04d}, name='{self.name}')>"