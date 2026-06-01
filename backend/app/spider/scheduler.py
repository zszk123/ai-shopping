"""定时爬虫调度器 - 后台定时采集热门商品"""
import asyncio
from datetime import datetime

from app.spider.douyin_crawler import DouyinCrawler
from app.spider.jd_crawler import JDCrawler
from app.spider.pdd_crawler import PDDCrawler
from app.spider.taobao_crawler import TaobaoCrawler

# 热门商品关键词 - 定期轮询采集
HOT_KEYWORDS = [
    "iPhone 16 Pro Max",
    "华为Mate 70 Pro",
    "小米15 Ultra",
    "MacBook Pro",
    "AirPods Pro",
    "耐克运动鞋",
    "阿迪达斯",
    "机械革命",
    "Switch游戏机",
    "戴森吸尘器",
    "戴尔笔记本",
    "联想笔记本",
    "海尔冰箱",
    "格力空调",
    "美的洗衣机",
    "SK-II神仙水",
    "兰蔻小黑瓶",
    "李宁跑鞋",
    "安踏篮球鞋",
    "PS5游戏机",
]

CRAWLER_MAP = {
    "淘宝": TaobaoCrawler,
    "京东": JDCrawler,
    "拼多多": PDDCrawler,
    "抖音": DouyinCrawler,
}


async def crawl_platform(platform: str, keyword: str) -> dict:
    """单个平台 + 关键词的采集任务"""
    crawler_cls = CRAWLER_MAP.get(platform)
    if not crawler_cls:
        return {"platform": platform, "keyword": keyword, "status": "unknown_platform"}

    crawler = crawler_cls()
    try:
        goods_list = await crawler.search(keyword, page=1)
        result = await crawler.push_to_server(goods_list)
        return {
            "platform": platform,
            "keyword": keyword,
            "status": "ok",
            "count": len(goods_list),
            "pushed": len([r for r in result if "goods_id" in r]),
        }
    except Exception as e:
        return {"platform": platform, "keyword": keyword, "status": "error", "error": str(e)}
    finally:
        await crawler.aclose()


async def crawl_keyword(keyword: str) -> list[dict]:
    """采集单个关键词的所有平台"""
    tasks = [crawl_platform(platform, keyword) for platform in CRAWLER_MAP]
    return await asyncio.gather(*tasks)


async def run_daily_crawl():
    """每日全量采集 - 所有关键词 × 所有平台"""
    print(f"[{datetime.now()}] 开始每日全量采集...")
    all_results = []
    for keyword in HOT_KEYWORDS:
        results = await crawl_keyword(keyword)
        all_results.extend(results)
        total = sum(r.get("count", 0) for r in results)
        print(f"  关键词 [{keyword}] 采集完成, 共 {total} 条")
        await asyncio.sleep(5)  # 爬完一组休眠，避免触发风控
    print(f"[{datetime.now()}] 每日采集完成, 共 {len(all_results)} 个任务")
    return all_results


async def run_incremental_crawl(keywords: list[str] | None = None):
    """增量采集 - 指定关键词"""
    targets = keywords or ["iPhone 16", "华为Mate"]
    all_results = []
    for keyword in targets:
        results = await crawl_keyword(keyword)
        all_results.extend(results)
    return all_results


async def start_scheduler():
    """启动循环调度器，在后台运行。首次启动延迟1小时，之后每6小时一轮。"""
    print(f"[{datetime.now()}] 爬虫调度器启动，1小时后开始首次采集")
    await asyncio.sleep(3600)  # 给服务器1小时初始化时间
    while True:
        await run_daily_crawl()
        await asyncio.sleep(6 * 3600)
