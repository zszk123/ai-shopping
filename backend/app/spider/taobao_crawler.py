"""淘宝爬虫 - Selenium + Edge 无头浏览器

淘宝反爬极为严格，优先尝试移动端/h5页面，失败则回退到mock数据。
"""
from app.spider.base_crawler import BaseCrawler
from app.spider.mock_data import generate_mock_goods


class TaobaoCrawler(BaseCrawler):
    platform = "淘宝"
    base_url = "https://s.taobao.com/search"

    # ------------------------------------------------------------------
    # 关键词搜索
    # ------------------------------------------------------------------

    def crawl_by_keyword(self, keyword: str, page: int = 1) -> list[dict]:
        # 优先使用淘宝h5搜索页（反爬较弱）
        url = f"{self.base_url}?q={keyword}&s={(page - 1) * 44}&ie=utf8"
        print(f"[淘宝] 正在搜索: {url}")

        try:
            html = self._fetch_page(
                url,
                wait_selector="div[class*='Card']",
                wait_ms=5000,
            )
            items = self._parse_search(html)
            if items:
                print(f"[淘宝] 搜索成功: {len(items)} 条")
                return items
        except Exception as e:
            print(f"[淘宝] 搜索失败: {e}")

        print("[淘宝] 使用模拟数据")
        return generate_mock_goods(keyword, "淘宝", count=8)

    def _parse_search(self, html: str) -> list[dict]:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        items = []

        # 淘宝搜索页商品卡片 — 多种可能的CSS类名
        card_selectors = [
            ".Card--doubleCardWrapper--",
            ".card-item",
            "div[class*='Card--']",
            "div[class*='card']:has(img)",
            '[class*="Content--contentInner"] > div',
        ]

        cards = []
        for sel in card_selectors:
            cards = soup.select(sel)
            if cards:
                break

        for card in cards:
            try:
                img = card.select_one("img")
                title_el = (
                    card.select_one('[class*="Title--"]')
                    or card.select_one('[class*="title"]')
                    or card.select_one('span[class*="wordBreak"]')
                )
                price_int = card.select_one('[class*="Price--priceInt"]') or card.select_one('[class*="priceInt"]')
                price_dec = card.select_one('[class*="Price--priceFloat"]') or card.select_one('[class*="priceFloat"]')
                shop_el = (
                    card.select_one('[class*="ShopInfo--"]')
                    or card.select_one('[class*="shop"]')
                    or card.select_one('.seller')
                )
                sold_el = (
                    card.select_one('[class*="realSales"]')
                    or card.select_one('[class*="sales"]')
                    or card.select_one('[class*="sold"]')
                )
                link_el = card.select_one("a[href*='item.taobao.com']") or card.select_one("a")

                title_text = title_el.get_text(strip=True) if title_el else ""
                if not title_text or len(title_text) < 3:
                    continue

                # 价格拼接
                price = 0.0
                if price_int:
                    p = price_int.get_text(strip=True)
                    if price_dec:
                        p += "." + price_dec.get_text(strip=True)
                    price = self._parse_price(p)

                # 图片
                img_src = ""
                if img:
                    img_src = img.get("src") or img.get("data-src") or img.get("data-ks-lazyload") or ""
                    if img_src.startswith("//"):
                        img_src = "https:" + img_src

                # 链接
                goods_url = ""
                if link_el:
                    goods_url = link_el.get("href", "")
                    if goods_url.startswith("//"):
                        goods_url = "https:" + goods_url

                items.append({
                    "goods_name": title_text,
                    "brand": self._extract_brand(title_text),
                    "model": "",
                    "spec_param": "",
                    "shop_name": shop_el.get_text(strip=True) if shop_el else "",
                    "original_price": price,
                    "real_price": price,
                    "coupon_desc": "",
                    "goods_img": img_src,
                    "goods_url": goods_url,
                    "sales_num": self._parse_taobao_sales(sold_el),
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
        """爬取淘宝商品详情页"""
        print(f"[淘宝] 正在爬取详情: {link}")
        try:
            html = self._fetch_page(link, wait_selector="h1", wait_ms=4000)
            return self._parse_detail(html, link)
        except Exception as e:
            print(f"[淘宝] 详情爬取失败: {e}")
            return {}

    def _parse_detail(self, html: str, link: str) -> dict:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")

        title_el = (
            soup.select_one(".tb-main-title")
            or soup.select_one("h1[data-spm]")
            or soup.select_one("h1")
        )
        price_el = (
            soup.select_one(".tm-price")
            or soup.select_one(".tb-rmb-num")
            or soup.select_one('[class*="price"]')
        )
        img_el = soup.select_one("#J_ImgBooth") or soup.select_one(".tb-gallery img")
        shop_el = (
            soup.select_one(".tb-shop-name a")
            or soup.select_one('[class*="shop"] a')
        )

        title_text = title_el.get_text(strip=True) if title_el else ""

        img_src = ""
        if img_el:
            img_src = img_el.get("src") or img_el.get("data-src") or ""
            if img_src.startswith("//"):
                img_src = "https:" + img_src

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
            "华为", "小米", "OPPO", "vivo", "三星", "苹果", "海尔", "美的", "格力",
            "戴尔", "联想", "惠普", "华硕", "荣耀", "一加", "真我", "索尼",
            "海信", "TCL", "长虹", "松下", "飞利浦", "西门子", "博世",
            "戴森", "科沃斯", "石头", "追觅",
            "耐克", "阿迪达斯", "李宁", "安踏", "斐乐", "斯凯奇", "New Balance",
        ]
        for b in sorted(brands, key=len, reverse=True):
            if b.lower() in title.lower():
                return b
        return ""

    def _parse_taobao_sales(self, el) -> int:
        if not el:
            return 0
        text = el.get_text(strip=True)
        return self._parse_sales(text)
