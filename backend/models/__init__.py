from sqlalchemy.ext.asyncio import create_async_engine
from setting import DATABASE_URL

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData

# 创建异步引擎
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_size=10,
    max_overflow=20,
)

AsyncSessionFactory = sessionmaker(
    bind=engine,  # Engine或者子类对象
    expire_on_commit=False,  # 是否在执行commit操作后session就过期
    class_=AsyncSession, #session类的替代
    autoflush=True   # 是否在查找之前flush
    )

class Base(DeclarativeBase):
    metadata = MetaData(naming_convention={
        # ix:index
        "ix":'ix_%(column_0_label)s',
        # un:
        "uq":'uq_%(table_name)s_%(column_0_name)s',
        #
        "ck":'ck_%(table_name)s_%(constraint_name)s',
        "fk":'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
        "pk":'pk_%(table_name)s',
    })

from . import user
from . import teacher
from . import student
from . import course
from . import course_class
from . import emailcode
from . import question
from . import temp_question
from . import assignment
from . import class_student
from . import class_assignment
from . import student_submission