from fastapi import APIRouter, Depends, Query

from app.dependencies import require_internal_token
from app.spider.scheduler import HOT_KEYWORDS, crawl_keyword, run_daily_crawl
from app.utils.response import fail, success

router = APIRouter(prefix="/api/spider", tags=["spider"], dependencies=[Depends(require_internal_token)])


@router.post("/daily")
async def trigger_daily_crawl():
    try:
        results = await run_daily_crawl()
        success_count = sum(1 for r in results if r["status"] == "ok")
        return success(data={"total": len(results), "success": success_count, "results": results})
    except Exception as e:
        return fail(msg=f"Crawl failed: {str(e)}", code=500)


@router.post("/keyword")
async def trigger_keyword_crawl(keyword: str = Query(..., min_length=1, max_length=100)):
    try:
        results = await crawl_keyword(keyword)
        return success(data={"keyword": keyword, "results": results})
    except Exception as e:
        return fail(msg=f"Crawl failed: {str(e)}", code=500)


@router.get("/keywords")
async def get_hot_keywords():
    return success(data={"keywords": HOT_KEYWORDS})
