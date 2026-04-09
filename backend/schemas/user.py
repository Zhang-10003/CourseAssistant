from pydantic import BaseModel,EmailStr,Field
from typing import Annotated


class RegisterIn(BaseModel):
    email: EmailStr
    username: Annotated[str,Field(min_length=1,max_length=10,description='用户名')]
    password: Annotated[str,Field(min_length=1,max_length=10,description='密码')]

# 登录参数
class LoginIn(BaseModel):
    username: Annotated[str,Field(min_length=1,max_length=10,description='用户名')]
    password: Annotated[str,Field(min_length=1,max_length=10,description='密码')]

# 创建用户
class UserCreateSchema(BaseModel):
    username: Annotated[str,Field(min_length=1,max_length=10,description='<UNK>')]
    password: Annotated[str,Field(min_length=1,max_length=10,description='<UNK>')]
    user_type:int

class StudentClassResponse(BaseModel):
    class_name: str
    class_id:int
    total_students: int

    class Config:
        from_attributes = True