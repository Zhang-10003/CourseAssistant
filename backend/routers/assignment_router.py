from fastapi import APIRouter, Depends, HTTPException
from services.assignment_service import create_assignment_from_temp
from schemas.assignment import AssignmentCreate
from dependencies import get_session
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/assignment", tags=["assignment"])


@router.post("/create")
async def create_assignment_endpoint(
        request: AssignmentCreate,
        db: AsyncSession = Depends(get_session)
):
    # 逻辑：只要调用此接口，后端就去 temp_question 扫货，全抓过来
    assignment = await create_assignment_from_temp(db, request)

    if not assignment:
        raise HTTPException(status_code=400, detail="临时题目库为空，请先调用 AI 生成题目")

    return {
        "code": 200,
        "message": "作业创建成功",
        "data": {
            "assignment_id": assignment.id,
            "question_count": len(assignment.question_ids)
        }
    }