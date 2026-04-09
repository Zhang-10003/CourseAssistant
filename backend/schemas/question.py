from pydantic import BaseModel, Field
from typing import List, Optional

class AIRequest(BaseModel):
    """前端请求 AI 生成题目的参数：仅需一个字符串指令"""
    input: str = Field(..., description="例如：帮我出3道计算机网络的选择题", example="出2道Python基础题")

class QuestionSchema(BaseModel):
    q_type: int = Field(description="题目类型：0为单选题，1为多选题，2为简答题")
    content: str = Field(description="题干内容")
    options_data: Optional[List[str]] = Field(
        default=None,
        description="选项列表。q_type为0或1时必填（4个字符串）；q_type为2时为null"
    )
    # 核心：索引列表格式
    correct_answer: List[int] = Field(
        description="正确答案索引列表（从0开始）。单选如[0]，多选如[0,2]，简答题为[]"
    )
    analysis: Optional[str] = Field(description="解析。简答题请在此包含参考答案")
    points: int = Field(default=5, description="分值")

class AIQuestionResponse(BaseModel):
    questions: List[QuestionSchema]