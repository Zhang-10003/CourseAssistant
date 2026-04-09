from pydantic import BaseModel,Field
from typing import Any, Optional, Generic, TypeVar

# from typing import Annotated , Literal
# class ResponseOut(BaseModel):
#     result: Annotated[Literal["success","failure"],Field("success",description="操作的结果:")]

T = TypeVar("T")

class ResponseOut(BaseModel, Generic[T]):
    code: str = Field(..., description="业务状态码")
    message: str = Field(..., description="响应消息")
    data: Optional[T] = Field(None, description="响应数据")

    @staticmethod
    def success(data: Any = None, message: str = "success"):
        return {"code": "000", "message": message, "data": data}

    @staticmethod
    def fail(code: str = "001", message: str = "error", data: Any = None):
        return {"code": code, "message": message, "data": data}

# 导出其他模块
from . import user
from . import question