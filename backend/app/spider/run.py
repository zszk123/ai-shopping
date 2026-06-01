"""爬虫CLI入口 - 手动触发采集任务

用法:
    python -m app.spider.run daily           # 执行每日全量采集
    python -m app.spider.run incremental     # 增量采集（热门关键词）
    python -m app.spider.run search "iPhone" # 按关键词采集
    python -m app.spider.run scheduler       # 启动调度器，持续运行
    python -m app.spider.run platform 淘宝 "iPhone 16"  # 指定平台+关键词
"""
import asyncio
import sys

from app.spider.scheduler import (
    CRAWLER_MAP,
    HOT_KEYWORDS,
    crawl_platform,
    run_daily_crawl,
    run_incremental_crawl,
)


async def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1]

    if cmd == "daily":
        print("=== 执行每日全量采集 ===")
        results = await run_daily_crawl()
        success = sum(1 for r in results if r["status"] == "ok")
        fail = sum(1 for r in results if r["status"] != "ok")
        print(f"完成: {success} 成功, {fail} 失败")

    elif cmd == "incremental":
        print("=== 增量采集（前5个热门关键词）===")
        results = await run_incremental_crawl(HOT_KEYWORDS[:5])
        for r in results:
            print(f"  {r['platform']} | {r['keyword']} | {r['status']} | {r.get('count', 0)} 条")

    elif cmd == "search":
        if len(sys.argv) < 3:
            print("请提供关键词: python -m app.spider.run search \"iPhone\"")
            return
        keyword = sys.argv[2]
        print(f"=== 搜索采集: {keyword} ===")
        results = await run_incremental_crawl([keyword])
        for r in results:
            print(f"  {r['platform']} | {r['status']} | {r.get('count', 0)} 条")

    elif cmd == "scheduler":
        print("=== 启动调度器（每6小时执行一次）===")
        from app.spider.scheduler import start_scheduler
        await start_scheduler()

    elif cmd == "platform":
        if len(sys.argv) < 4:
            print("请提供平台和关键词: python -m app.spider.run platform 淘宝 \"iPhone 16\"")
            return
        platform = sys.argv[2]
        keyword = sys.argv[3]
        if platform not in CRAWLER_MAP:
            print(f"未知平台: {platform}，可用: {list(CRAWLER_MAP.keys())}")
            return
        result = await crawl_platform(platform, keyword)
        print(result)


if __name__ == "__main__":
    asyncio.run(main())
