from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user_id
from app.schemas.compare import UrlCompareReq
from app.services import compare_service
from app.utils.image_validation import MAX_IMAGE_SIZE, is_supported_image
from app.utils.response import fail, success

router = APIRouter(prefix="/api/compare", tags=["compare"])


@router.post("/image")
async def compare_by_image(
    file: UploadFile = File(...),
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

    try:
        result = await compare_service.compare_by_upload(db, file_bytes, user_id)
        return success(data=result)
    except RuntimeError as e:
        return fail(msg=f"Image compare failed: {str(e)}", code=500)
    except ValueError as e:
        return fail(msg=f"Invalid image compare request: {str(e)}", code=400)


@router.post("/url")
async def compare_by_url(
    req: UrlCompareReq,
    db: AsyncSession = Depends(get_db),
    user_id: int | None = Depends(get_current_user_id),
):
    try:
        result = await compare_service.compare_by_url(db, str(req.goods_url), user_id)
        return success(data=result)
    except RuntimeError as e:
        return fail(msg=f"URL compare failed: {str(e)}", code=500)
    except ValueError as e:
        return fail(msg=f"Invalid URL compare request: {str(e)}", code=400)


@router.get("/search")
async def compare_by_keyword(
    keyword: str,
    db: AsyncSession = Depends(get_db),
    user_id: int | None = Depends(get_current_user_id),
):
    try:
        result = await compare_service.compare_by_keyword(db, keyword, user_id)
        return success(data=result)
    except RuntimeError as e:
        return fail(msg=f"Keyword compare failed: {str(e)}", code=500)
    except ValueError as e:
        return fail(msg=f"Invalid keyword compare request: {str(e)}", code=400)
