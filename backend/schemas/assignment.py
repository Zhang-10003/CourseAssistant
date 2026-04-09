from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime

class AssignmentCreate(BaseModel):
    user_id: int = Field(..., description="所属用户 ID")  # 新增字段
    title: str = Field(..., description="作业标题")
    deadline: Optional[datetime] = Field(None, description="截止时间，格式：YYYY-M-D HH:mm")

    @field_validator('deadline', mode='before')
    @classmethod
    def parse_custom_datetime(cls, v):
        if isinstance(v, str) and v.strip():
            try:
                # 解析你要求的格式：2026-3-19 13:24
                # %Y-%m-%d %H:%M 可以兼容 2026-3-19 和 2026-03-19
                return datetime.strptime(v, "%Y-%m-%d %H:%M")
            except ValueError:
                raise ValueError("时间格式错误，请使用 'YYYY-M-D HH:mm' 格式 (例如: 2026-3-19 13:24)")
        return v

class AssignmentResponse(BaseModel):
    id: int
    title: str
    created_at: datetime
    deadline: Optional[datetime]
    question_ids: List[int]

    class Config:
        from_attributes = True


class ClassAssignmentListItem(BaseModel):
    id: int = Field(..., description="发布记录 ID")
    assignment_id: int = Field(..., description="原始作业模板 ID")
    title: str
    max_score: int
    start_at: str  # 因为 service 层做了 strftime 格式化
    end_at: str
    class Config:
        from_attributes = True