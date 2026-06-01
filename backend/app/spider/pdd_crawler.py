"""拼多多爬虫 - Selenium + Edge 无头浏览器

使用拼多多移动端页面，结构相对简单，反爬力度较低。
"""
from app.spider.base_crawler import BaseCrawler
from app.spider.mock_data import generate_mock_goods


class PDDCrawler(BaseCrawler):
    platform = "拼多多"
    base_url = "https://mobile.yangkeduo.com/search_result.html"

    # ------------------------------------------------------------------
    # 关键词搜索
    # ------------------------------------------------------------------

    def crawl_by_keyword(self, keyword: str, page: int = 1) -> list[dict]:
        url = f"{self.base_url}?search_key={keyword}&page={page}"
        print(f"[拼多多] 正在搜索: {url}")

        try:
            html = self._fetch_page(
                url,
                wait_selector=".search-res-container .goods-item",
                wait_ms=4000,
            )
            items = self._parse_search(html)
            if items:
                print(f"[拼多多] 搜索成功: {len(items)} 条")
                return items
        except Exception as e:
            print(f"[拼多多] 搜索失败: {e}")

        print("[拼多多] 使用模拟数据")
        return generate_mock_goods(keyword, "拼多多", count=8)

    def _parse_search(self, html: str) -> list[dict]:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        items = []

        for card in soup.select(".search-res-container .goods-item, .goods-list .goods-item, div[class*='goods-item']"):
            try:
                img = card.select_one("img")
                title_el = (
                    card.select_one(".goods-title")
                    or card.select_one(".goods-name")
                    or card.select_one(".title")
                )
                price_el = (
                    card.select_one(".goods-price")
                    or card.select_one(".price")
                    or card.select_one("[class*='price']")
                )
                shop_el = (
                    card.select_one(".mall-title")
                    or card.select_one(".shop-name")
                    or card.select_one(".seller-name")
                )
                link_el = card.select_one("a")

                title_text = title_el.get_text(strip=True) if title_el else ""
                if not title_text or len(title_text) < 3:
                    continue

                img_src = ""
                if img:
                    img_src = img.get("src") or img.get("data-src") or ""
                    if img_src.startswith("//"):
                        img_src = "https:" + img_src

                goods_url = ""
                if link_el:
                    href = link_el.get("href", "")
                    if href.startswith("//"):
                        goods_url = "https:" + href
                    elif href.startswith("/"):
                        goods_url = "https://mobile.yangkeduo.com" + href
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
        """爬取拼多多商品详情页"""
        print(f"[拼多多] 正在爬取详情: {link}")
        try:
            html = self._fetch_page(link, wait_selector=".goods-name", wait_ms=4000)
            return self._parse_detail(html, link)
        except Exception as e:
            print(f"[拼多多] 详情爬取失败: {e}")
            return {}

    def _parse_detail(self, html: str, link: str) -> dict:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")

        title_el = (
            soup.select_one(".goods-name")
            or soup.select_one(".title")
            or soup.select_one("h1")
        )
        price_el = (
            soup.select_one(".goods-price")
            or soup.select_one(".price")
            or soup.select_one("[class*='price']")
        )
        img_el = soup.select_one(".goods-img img") or soup.select_one(".img-wrap img")
        shop_el = (
            soup.select_one(".mall-name")
            or soup.select_one(".shop-name")
            or soup.select_one(".seller")
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
            "华为", "小米", "苹果", "OPPO", "vivo", "三星", "海尔", "美的", "格力",
            "戴尔", "联想", "惠普", "华硕", "荣耀", "索尼", "海信", "TCL", "长虹",
            "松下", "飞利浦", "苏泊尔", "九阳", "方太", "老板", "科沃斯",
            "戴森", "石头", "追觅", "添可",
            "耐克", "阿迪达斯", "李宁", "安踏", "斐乐", "斯凯奇", "回力",
            "SK-II", "兰蔻", "雅诗兰黛", "资生堂",
        ]
        for b in sorted(brands, key=len, reverse=True):
            if b.lower() in title.lower():
                return b
        return ""
