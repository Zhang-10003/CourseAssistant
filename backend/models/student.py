from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from models import Base

class Student(Base):
    __tablename__ = 'students'

    # 1. student_id: 既是主键，又是外键，指向 user 表的 id
    student_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user.user_id"),
        primary_key=True,
        nullable=False
    )

    # 2. student_no: 唯一且自增
    # 注意：MySQL 默认从 1 开始，若需 0000 效果，建议在数据库初始化后
    # 执行 ALTER TABLE teachers AUTO_INCREMENT = 0; (取决于数据库版本支持)
    student_no: Mapped[int] = mapped_column(
        Integer,
        unique=True,
        autoincrement=True,
        nullable=False
    )

    # 3. name & email: 非空
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    def __repr__(self) -> str:
        # 在控制台打印时自动展示 5 位格式化后的编号
        return f"<Student(id={self.student_id}, no={self.student_no:05d}, name='{self.name}')>"