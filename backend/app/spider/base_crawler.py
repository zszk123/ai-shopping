"""爬虫基类 - Selenium + Windows Edge 无头浏览器"""
import asyncio
import random
import re
import time
from abc import ABC, abstractmethod

import httpx
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) EdgiOS/131.0.0.0 Mobile/15E148",
]


class BaseCrawler(ABC):
    """爬虫基类 - Selenium + Edge 无头浏览器

    核心方法:
        crawl_by_keyword(keyword, page) → list[dict]  关键词搜索
        crawl_by_link(link) → dict                    商品详情页爬取
    """

    platform: str = ""
    api_base: str = "http://127.0.0.1:8000/api"

    def __init__(self, use_proxy: bool = False, proxy_url: str = ""):
        self.use_proxy = use_proxy
        self.proxy_url = proxy_url
        self._driver: webdriver.Edge | None = None
        self._http: httpx.AsyncClient | None = None

    # ------------------------------------------------------------------
    # 浏览器管理
    # ------------------------------------------------------------------

    def _init_driver(self):
        """初始化无头Edge浏览器，静默运行不弹窗"""
        options = EdgeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--lang=zh-CN")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-notifications")
        options.add_argument("--mute-audio")
        options.add_argument("--disable-logging")
        options.add_argument("--log-level=3")
        options.add_argument("--output=/dev/null")

        # 随机UA
        ua = random.choice(USER_AGENTS)
        options.add_argument(f"--user-agent={ua}")

        # 隐藏自动化标记
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        # 代理
        if self.use_proxy and self.proxy_url:
            options.add_argument(f"--proxy-server={self.proxy_url}")

        prefs = {
            "profile.default_content_setting_values.images": 1,
            "profile.managed_default_content_settings.stylesheets": 1,
        }
        options.add_experimental_option("prefs", prefs)

        try:
            self._driver = webdriver.Edge(options=options)
        except WebDriverException as e:
            raise RuntimeError(
                f"Edge WebDriver 初始化失败。请确认:\n"
                f"  1. Edge浏览器已安装 (Win11自带)\n"
                f"  2. 网络可访问 (首次需自动下载 msedgedriver)\n"
                f"  原始错误: {e}"
            )

        # CDP 反检测脚本 — 页面加载前注入
        self._driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                Object.defineProperty(navigator, 'languages', {get: () => ['zh-CN', 'zh', 'en']});
                Object.defineProperty(navigator, 'hardwareConcurrency', {get: () => 8});
                window.chrome = {runtime: {}};
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                    Promise.resolve({state: Notification.permission}) :
                    originalQuery(parameters)
                );
            """
        })

    def _ensure_driver(self):
        if self._driver is None:
            self._init_driver()

    # ------------------------------------------------------------------
    # 页面加载
    # ------------------------------------------------------------------

    def _fetch_page(self, url: str, wait_selector: str = "", wait_ms: int = 3000) -> str:
        """加载页面等待JS渲染，返回完整HTML

        Args:
            url: 目标URL
            wait_selector: CSS选择器，等待该元素出现（可选）
            wait_ms: 额外等待毫秒数（让动态内容加载完）
        """
        self._ensure_driver()
        self._driver.get(url)
        time.sleep(wait_ms / 1000.0)

        if wait_selector:
            try:
                WebDriverWait(self._driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, wait_selector))
                )
            except TimeoutException:
                pass

        # 模拟人类滚动行为
        for _ in range(random.randint(1, 3)):
            self._driver.execute_script(
                f"window.scrollBy(0, {random.randint(200, 600)})"
            )
            time.sleep(random.uniform(0.3, 0.8))

        return self._driver.page_source

    def _safe_find_elements(self, css: str, timeout: int = 5):
        """安全查找元素，超时返回空列表"""
        self._ensure_driver()
        try:
            WebDriverWait(self._driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, css))
            )
            return self._driver.find_elements(By.CSS_SELECTOR, css)
        except TimeoutException:
            return []

    def _safe_find_text(self, css: str, default: str = "") -> str:
        """安全获取单个元素文本"""
        try:
            el = self._driver.find_element(By.CSS_SELECTOR, css)
            return el.text.strip()
        except Exception:
            return default

    def _safe_find_attr(self, css: str, attr: str, default: str = "") -> str:
        """安全获取单个元素属性"""
        try:
            el = self._driver.find_element(By.CSS_SELECTOR, css)
            return el.get_attribute(attr) or default
        except Exception:
            return default

    # ------------------------------------------------------------------
    # 核心爬取方法（子类必须实现）
    # ------------------------------------------------------------------

    @abstractmethod
    def crawl_by_keyword(self, keyword: str, page: int = 1) -> list[dict]:
        """按关键词搜索商品，返回商品列表"""
        ...

    @abstractmethod
    def crawl_by_link(self, link: str) -> dict:
        """按商品链接爬取商品详情，返回单个商品信息"""
        ...

    # ------------------------------------------------------------------
    # 异步包装器（兼容 FastAPI 异步环境）
    # ------------------------------------------------------------------

    async def search(self, keyword: str, page: int = 1) -> list[dict]:
        """异步关键词搜索 — 在线程池运行同步Selenium，不阻塞事件循环"""
        try:
            return await asyncio.to_thread(self.crawl_by_keyword, keyword, page)
        except Exception as e:
            print(f"[{self.platform}] crawl_by_keyword 失败: {e}")
            return []

    async def fetch_detail(self, link: str) -> dict:
        """异步商品详情爬取"""
        try:
            return await asyncio.to_thread(self.crawl_by_link, link)
        except Exception as e:
            print(f"[{self.platform}] crawl_by_link 失败: {e}")
            return {}

    # ------------------------------------------------------------------
    # 工具方法
    # ------------------------------------------------------------------

    def _normalize(self, raw: dict) -> dict:
        return {
            "goods_name": str(raw.get("goods_name", "")),
            "brand": str(raw.get("brand", "")),
            "model": str(raw.get("model", "")),
            "spec_param": str(raw.get("spec_param", "")),
            "platform": self.platform,
            "shop_name": str(raw.get("shop_name", "")),
            "original_price": float(raw.get("original_price", 0) or 0),
            "real_price": float(raw.get("real_price", 0) or 0),
            "coupon_desc": str(raw.get("coupon_desc", "")),
            "goods_img": str(raw.get("goods_img", "")),
            "goods_url": str(raw.get("goods_url", "")),
            "sales_num": int(raw.get("sales_num", 0) or 0),
            "score": float(raw.get("score", 0) or 0),
            "sale_status": 1,
        }

    @staticmethod
    def _parse_price(price_str) -> float:
        if not price_str:
            return 0.0
        nums = re.findall(r"\d+\.?\d*", str(price_str).replace(",", ""))
        return float(nums[0]) if nums else 0.0

    def _parse_sales(self, text: str) -> int:
        """解析销量文本 -> 整数"""
        if not text:
            return 0
        nums = re.findall(r"\d+\.?\d*", text)
        if not nums:
            return 0
        num = float(nums[0])
        if "万" in text or "w" in text.lower():
            num *= 10000
        return int(num)

    async def _get_http(self) -> httpx.AsyncClient:
        if self._http is None:
            self._http = httpx.AsyncClient(
                headers={"User-Agent": random.choice(USER_AGENTS)},
                timeout=30,
                follow_redirects=True,
            )
        return self._http

    async def push_to_server(self, goods_list: list[dict]) -> list[dict]:
        """将采集结果通过内部接口写入数据库"""
        results = []
        http = await self._get_http()
        for item in goods_list:
            normalized = self._normalize(item)
            try:
                resp = await http.post(
                    f"{self.api_base}/spider/add_goods", json=normalized
                )
                data = resp.json()
                results.append(data.get("data", {}))
            except Exception as e:
                results.append({
                    "error": str(e),
                    "goods_name": normalized["goods_name"],
                })
            await asyncio.sleep(0.3)
        return results

    def close(self):
        """关闭浏览器和HTTP客户端"""
        if self._driver:
            try:
                self._driver.quit()
            except Exception:
                pass
            self._driver = None

    async def aclose(self):
        """异步关闭（供调度器调用）"""
        self.close()
        if self._http:
            await self._http.aclose()
            self._http = None
