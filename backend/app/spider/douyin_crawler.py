"""抖音电商爬虫 - Selenium + Edge 无头浏览器

抖音电商是纯SPA应用，必须用真实浏览器渲染后才能拿到DOM。
"""
from app.spider.base_crawler import BaseCrawler
from app.spider.mock_data import generate_mock_goods


class DouyinCrawler(BaseCrawler):
    platform = "抖音"
    base_url = "https://haohuo.jinritemai.com/views/search"

    # ------------------------------------------------------------------
    # 关键词搜索
    # ------------------------------------------------------------------

    def crawl_by_keyword(self, keyword: str, page: int = 1) -> list[dict]:
        url = f"{self.base_url}?keyword={keyword}&page={page}"
        print(f"[抖音] 正在搜索: {url}")

        try:
            html = self._fetch_page(
                url,
                wait_selector="[class*='product'], [class*='card'], [class*='item']",
                wait_ms=5000,
            )
            items = self._parse_search(html)
            if items:
                print(f"[抖音] 搜索成功: {len(items)} 条")
                return items
        except Exception as e:
            print(f"[抖音] 搜索失败: {e}")

        print("[抖音] 使用模拟数据")
        return generate_mock_goods(keyword, "抖音", count=8)

    def _parse_search(self, html: str) -> list[dict]:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        items = []

        for card in soup.select(
            "[class*='product-card'], "
            "[class*='ProductCard'], "
            "[class*='search-item'], "
            "[class*='card-item'], "
            "a[href*='product']"
        ):
            try:
                img = card.select_one("img")
                title_el = card.select_one("[class*='title'], [class*='name']")
                price_el = card.select_one("[class*='price'], [class*='Price']")
                shop_el = card.select_one(
                    "[class*='shop'], [class*='seller'], [class*='author']"
                )
                link_el = card.select_one("a") if card.name != "a" else card

                title_text = title_el.get_text(strip=True) if title_el else ""
                if not title_text or len(title_text) < 3:
                    continue

                img_src = ""
                if img:
                    img_src = img.get("src") or img.get("data-src") or ""

                goods_url = ""
                if link_el:
                    href = link_el.get("href", "")
                    if href.startswith("//"):
                        goods_url = "https:" + href
                    elif href.startswith("/"):
                        goods_url = "https://haohuo.jinritemai.com" + href
                    else:
                        goods_url = href

                items.append({
                    "goods_name": title_text,
                    "brand": self._extract_brand(title_text),
                    "model": "",
                    "spec_param": "",
                    "shop_name": shop_el.get_text(strip=True) if shop_el else "",
                    "original_price": self._parse_price(price_el),
                    "real_price": self._parse_price(price_el),
                    "coupon_desc": "",
                    "goods_img": img_src,
                    "goods_url": goods_url,
                    "sales_num": 0,
                    "score": 0,
                    "sale_status": 1,
                })
            except Exception:
                continue

        return items

    # ------------------------------------------------------------------
    # 商品详情爬取
    # ------------------------------------------------------------------

    def crawl_by_link(self, link: str) -> dict:
        """爬取抖音商品详情页"""
        print(f"[抖音] 正在爬取详情: {link}")
        try:
            html = self._fetch_page(
                link,
                wait_selector="[class*='product'], [class*='detail']",
                wait_ms=5000,
            )
            return self._parse_detail(html, link)
        except Exception as e:
            print(f"[抖音] 详情爬取失败: {e}")
            return {}

    def _parse_detail(self, html: str, link: str) -> dict:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")

        title_el = (
            soup.select_one(".product-title")
            or soup.select_one("[class*='title']")
            or soup.select_one("h1")
        )
        price_el = (
            soup.select_one(".price-text")
            or soup.select_one(".product-price")
            or soup.select_one("[class*='price']")
        )
        img_el = (
            soup.select_one(".product-image img")
            or soup.select_one("[class*='cover'] img")
            or soup.select_one("img")
        )
        shop_el = (
            soup.select_one(".shop-name")
            or soup.select_one("[class*='shop']")
            or soup.select_one("[class*='seller']")
        )

        title_text = title_el.get_text(strip=True) if title_el else ""

        img_src = ""
        if img_el:
            img_src = img_el.get("src") or img_el.get("data-src") or ""

        return {
            "goods_name": title_text,
            "brand": self._extract_brand(title_text),
            "model": "",
            "spec_param": "",
            "shop_name": shop_el.get_text(strip=True) if shop_el else "",
            "original_price": self._parse_price(price_el),
            "real_price": self._parse_price(price_el),
            "coupon_desc": "",
            "goods_img": img_src,
            "goods_url": link,
            "sales_num": 0,
            "score": 0,
            "sale_status": 1,
        }

    # ------------------------------------------------------------------
    # 工具方法
    # ------------------------------------------------------------------

    def _extract_brand(self, title: str) -> str:
        brands = [
            "华为", "小米", "苹果", "OPPO", "vivo", "三星", "海尔", "美的", "格力",
            "戴尔", "联想", "惠普", "华硕", "荣耀", "索尼",
            "耐克", "阿迪达斯", "李宁", "安踏", "斐乐", "斯凯奇",
            "罗技", "雷蛇", "漫步者", "戴森",
        ]
        for b in sorted(brands, key=len, reverse=True):
            if b.lower() in title.lower():
                return b
        return ""
