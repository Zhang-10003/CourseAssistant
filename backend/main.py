from smtplib import SMTPResponseException

from fastapi_mail import FastMail,MessageSchema,MessageType
from fastapi import Depends
from dependencies import get_mail
from aiosmtplib import SMTP
from core.scheduler import scheduler
from contextlib import asynccontextmanager

# 导入router
from routers.auth_router import router as auth_router
from routers.question_router import router as question_router
from routers.assignment_router import router as assignment_router
from routers.teacher_router import router as teacher_router
from routers.student_router import router as student_router

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from schemas import ResponseOut

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 在主事件循环启动时开启调度器
    if not scheduler.running:
        scheduler.start()
    print("APScheduler (Async) 已在主循环中启动...")
    yield
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)

# --- 拦截所有报错并强制格式化 ---

# 1. 拦截主动抛出的 HTTPException (如 raise HTTPException(404))
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ResponseOut.fail(code="001", message=str(exc.detail))
    )

# 2. 拦截参数校验错误 (如前端传错字段，422 错误)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # 将 Pydantic 的错误详情放入 data，message 设为统一错误提示
    return JSONResponse(
        status_code=422,
        content=ResponseOut.fail(code="001", message="参数校验失败", data=exc.errors())
    )

# 3. 拦截未捕获的系统崩溃 (500 错误)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=ResponseOut.fail(code="001", message="服务器内部错误")
    )
# 配置允许跨域的列表
origins = [
    "http://localhost:5173",  # 你的前端地址
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,           # 允许的源
    allow_credentials=True,         # 允许携带 Cookie
    allow_methods=["*"],             # 允许所有方法 (GET, POST 等)
    allow_headers=["*"],             # 允许所有请求头 (Authorization 等)
)

app.include_router(auth_router)
app.include_router(question_router)
app.include_router(assignment_router)
app.include_router(teacher_router)
app.include_router(student_router)

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get('/mail/test')
async def mail_test(
    email:str,
    mail:FastMail=Depends(get_mail)
):
    message = MessageSchema(
        subject="课程管理小助手",
        recipients=[email],
        body=f"hello 你有一份作业请查收！！(嘻嘻）",
        subtype=MessageType.plain
    )
    try:
        await mail.send_message(message)
    except SMTPResponseException as e:
        if e.code == -1 and b"\\x00\\x00\\x00" in str(e).encode():
            print("忽略QQ邮箱SMTP关闭阶段的非标准响应（邮件已发送成功）")
    return {'message':"邮件发送成功"}

