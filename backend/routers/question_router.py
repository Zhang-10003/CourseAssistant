from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from dependencies import get_session
from models.temp_question  import TempQuestion
from schemas.question import AIRequest
from services.ai_service import generate_questions_with_langchain
from repository.question_repo import QuestionRepository

router = APIRouter(prefix="/question", tags=["question"])

@router.post("/ai-generate")
async def ai_generate_endpoint(request: AIRequest, db: AsyncSession = Depends(get_session)):
    try:
        # 1. AI 生成
        raw_questions = await generate_questions_with_langchain(request.input)

        # 2. 调用 Repository 存入临时表
        await QuestionRepository.save_to_temp(db, raw_questions)

        await db.commit()
        return {"code": 200, "message": "题目已生成至临时库", "data": raw_questions}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))