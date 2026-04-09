from fastapi_mail import FastMail,ConnectionConfig
from pydantic import SecretStr, EmailStr
import setting


def create_mail_instance() -> FastMail:
    """创建FastMail实例（每次调用返回新实例，线程/协程安全）"""
    mail_config = ConnectionConfig(
        MAIL_USERNAME=setting.MAIL_USERNAME,
        MAIL_PASSWORD=SecretStr(setting.MAIL_PASSWORD),
        MAIL_FROM=setting.MAIL_FROM,
        MAIL_PORT=setting.MAIL_PORT,
        MAIL_SERVER=setting.MAIL_SERVER,
        MAIL_FROM_NAME=setting.MAIL_FROM_NAME,
        MAIL_STARTTLS=setting.MAIL_STARTTLS,
        MAIL_SSL_TLS=setting.MAIL_SSL_TLS,
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True,
    )
    return FastMail(mail_config)