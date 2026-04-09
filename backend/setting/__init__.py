from datetime import timedelta

import os
from dotenv import load_dotenv

load_dotenv()

# 数据库相关配置
DATABASE_URL="mysql+aiomysql://root:123456@localhost:3306/course_assistant_db"

# 邮箱相关配置
MAIL_USERNAME = "1750404601@qq.com"
MAIL_PASSWORD = "skbmjczxbcjscdhe"
MAIL_FROM = "1750404601@qq.com"
MAIL_PORT = 587
MAIL_SERVER = "smtp.qq.com"
MAIL_FROM_NAME = "[课程助手]"
MAIL_STARTTLS = True
MAIL_SSL_TLS = False

# LLM相关配置
LLM_API_KEY = os.getenv("DASHSCOPE_API_KEY", "sk-5698481334c441c19600a51e41ac2d9b")
LLM_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
LLM_MODEL_NAME = "qwen-plus" # 智能出题的最稳选择

JWT_SECRET_KEY = "sfsadadafsjw32"
JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=15)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)