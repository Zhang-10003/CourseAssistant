from datetime import datetime

from sqlalchemy import String, Integer , DateTime
from sqlalchemy.orm import Mapped, mapped_column

from models import Base


class EmailCode(Base):
    __tablename__ = 'email_code'

    id:Mapped[int] = mapped_column(Integer, primary_key=True,autoincrement=True)
    email: Mapped[str] = mapped_column(String(50), nullable=False)
    code: Mapped[str] = mapped_column(String(10), nullable=False)
    create_time: Mapped[datetime] = mapped_column(DateTime)