import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from datetime import datetime, timezone
from enum import Enum
import setting
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN
from threading import Lock


class SingletonMeta(type):
    _instances = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class TokenTypeEnum(Enum):
    ACCESS_TOKEN = "access"
    REFRESH_TOKEN = "refresh"


class AuthHandler(metaclass=SingletonMeta):
    # auto_error=True 会在没有 Header 时自动返回 403，我们保持默认
    security = HTTPBearer()

    def _encode_token(self, user_id: int, token_type: TokenTypeEnum):
        # 遵循标准：sub 存用户标识，type 存类型
        payload = {
            "sub": str(user_id),
            "type": token_type.value,
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + (
                setting.JWT_ACCESS_TOKEN_EXPIRES if token_type == TokenTypeEnum.ACCESS_TOKEN
                else setting.JWT_REFRESH_TOKEN_EXPIRES
            )
        }
        # 直接传入字符串密钥，pyjwt 内部会自动处理
        return jwt.encode(payload, setting.JWT_SECRET_KEY, algorithm='HS256')

    def encode_login_token(self, user_id: int):
        return {
            "access_token": self._encode_token(user_id, TokenTypeEnum.ACCESS_TOKEN),
            "refresh_token": self._encode_token(user_id, TokenTypeEnum.REFRESH_TOKEN)
        }

    def decode_access_token(self, token: str):
        try:
            # 这里的密钥确保与 encode 时完全一致
            payload = jwt.decode(token, setting.JWT_SECRET_KEY, algorithms=['HS256'])

            # 校验 Token 类型
            if payload.get('type') != TokenTypeEnum.ACCESS_TOKEN.value:
                raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Token 类型错误!")

            return int(payload['sub'])

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Token 已过期，请重新登录")
        except jwt.InvalidTokenError as e:
            # 【调试关键】如果还报错，请看控制台打印的具体内容
            print(f"JWT Decode Error: {str(e)} | Token received: {token[:10]}...")
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="无效的 Token 凭证")

    async def auth_access_dependency(self, auth: HTTPAuthorizationCredentials = Security(security)):
        # auth.credentials 会自动剥离 "Bearer " 前缀，只拿加密串
        return self.decode_access_token(auth.credentials)