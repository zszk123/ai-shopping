from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user_id
from app.schemas.agent import AgentChatReq
from app.services import agent_service
from app.utils.image_validation import MAX_IMAGE_SIZE, is_supported_image
from app.utils.response import fail, success

router = APIRouter(prefix="/api/agent", tags=["agent"])


@router.post("/chat")
async def chat(
    req: AgentChatReq,
    db: AsyncSession = Depends(get_db),
    user_id: int | None = Depends(get_current_user_id),
):
    try:
        result = await agent_service.chat(db, req.message, user_id)
        return success(data=result)
    except ValueError as e:
        return fail(msg=str(e), code=400)
    except Exception as e:
        return fail(msg=f"Agent chat failed: {str(e)}", code=500)


@router.post("/chat/image")
async def chat_image(
    file: UploadFile = File(...),
    message: str = Form(default=""),
    db: AsyncSession = Depends(get_db),
    user_id: int | None = Depends(get_current_user_id),
):
    if not file.content_type or not file.content_type.startswith("image/"):
        return fail(msg="Only image files are supported", code=400)

    file_bytes = await file.read()
    if len(file_bytes) == 0:
        return fail(msg="Uploaded file is empty", code=400)
    if len(file_bytes) > MAX_IMAGE_SIZE:
        return fail(msg="Image size must not exceed 8MB", code=400)
    if not is_supported_image(file_bytes):
        return fail(msg="Only jpg, png and webp images are supported", code=400)

    result = await agent_service.chat_with_image(db, file_bytes, user_id, message)
    return success(data=result)
