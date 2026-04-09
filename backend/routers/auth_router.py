from fastapi import APIRouter, Query, Depends, HTTPException
from fastapi_mail import FastMail, MessageSchema, MessageType
from pydantic import EmailStr
from typing import Annotated
from smtplib import SMTPResponseException

from models import AsyncSession
from dependencies import get_mail, get_session

import string
import random

# --- 核心导入：引入你的 JWT 处理类 ---
from core.auth import AuthHandler
from models.user import User
from repository.user_repo import EmailCodeRepository, UserRepository
from schemas import ResponseOut
from schemas.user import LoginIn

router = APIRouter(prefix="/auth", tags=["auth"])

# 实例化单例 AuthHandler
auth_handler = AuthHandler()


@router.get('/code', response_model=ResponseOut)
async def get_email_code(
        email: Annotated[EmailStr, Query(...)],
        mail: FastMail = Depends(get_mail),
        session: AsyncSession = Depends(get_session)
):
    # 此处逻辑保持不变...
    source = string.digits * 4
    code = "".join(random.sample(source, 4))
    message = MessageSchema(
        subject="[毕设]验证码",
        recipients=[email],
        body=f"您的验证码为 {code}",
        subtype=MessageType.plain
    )
    try:
        await mail.send_message(message)
        # 成功发送后也需要存入数据库供后续校验
        email_code_repo = EmailCodeRepository(session=session)
        await email_code_repo.create(str(email), code)
    except SMTPResponseException as e:
        if e.code == -1 and b"\\x00\\x00\\x00" in str(e).encode():
            email_code_repo = EmailCodeRepository(session=session)
            await email_code_repo.create(str(email), code)
        else:
            raise HTTPException(status_code=500, detail="邮件发送失败")
    return ResponseOut(code="000", message="邮件发送成功", data="")

"""
    /auth/login : 用户登录api
"""
@router.post('/login')
async def login(data: LoginIn, session: AsyncSession = Depends(get_session)):
    user_repo = UserRepository(session=session)
    user = await user_repo.get_by_username(data.username)

    if not user or user.password != data.password:
        raise HTTPException(status_code=400, detail="用户名或密码错误")

    tokens = auth_handler.encode_login_token(user.user_id)

    return ResponseOut(
        code="000",
        message="登录成功",
        data={
            "token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "user_id": user.user_id,
            "user_type": user.user_type
        }
    )

"""
    /auth/user/{user_id}/name : 
"""
@router.get('/user/{user_id}/name')
async def get_user_name(
    user_id: int,
    # 使用修复后的依赖项
    current_user_id: int = Depends(auth_handler.auth_access_dependency),
    session: AsyncSession = Depends(get_session)
):
    user_repo = UserRepository(session=session)
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    real_name = await user_repo.get_real_name(user)
    return ResponseOut(
        code="000",
        message="查询成功",
        data={"name": real_name, "user_type": user.user_type}
    )