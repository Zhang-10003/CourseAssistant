from . import Base
from sqlalchemy.orm import Mapped,mapped_column
from sqlalchemy import Integer, String, DateTime

from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

class User(Base):
    __tablename__ = 'user'

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True,autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    _password: Mapped[str] = mapped_column(String(200), nullable=False)
    user_type:Mapped[int] = mapped_column(Integer,default=0)

    def __init__(self,*args,**kwargs):
        password = kwargs.pop('password')
        super().__init__(*args,**kwargs)
        if password:
            self.password = password

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self,raw_password):
        self._password = password_hash.hash(raw_password)

    def check_password(self,raw_password):
        return password_hash.verify(raw_password,self.password)

