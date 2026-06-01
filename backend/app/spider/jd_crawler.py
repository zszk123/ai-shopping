"""京东爬虫 - Selenium + Edge 无头浏览器"""
from app.spider.base_crawler import BaseCrawler
from app.spider.mock_data import generate_mock_goods


class JDCrawler(BaseCrawler):
    platform = "京东"
    base_url = "https://search.jd.com/Search"

    # ------------------------------------------------------------------
    # 关键词搜索
    # ------------------------------------------------------------------

    def crawl_by_keyword(self, keyword: str, page: int = 1) -> list[dict]:
        # 京东翻页是奇数: 1, 3, 5...
        jd_page = 2 * page - 1
        url = f"{self.base_url}?keyword={keyword}&page={jd_page}&enc=utf-8"
        print(f"[京东] 正在搜索: {url}")

        try:
            html = self._fetch_page(
                url,
                wait_selector=".gl-item",
                wait_ms=4000,
            )
            items = self._parse_search(html)
            if items:
                print(f"[京东] 搜索成功: {len(items)} 条")
                return items
        except Exception as e:
            print(f"[京东] 搜索失败: {e}")

        print("[京东] 使用模拟数据")
        return generate_mock_goods(keyword, "京东", count=8)

    def _parse_search(self, html: str) -> list[dict]:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        items = []

        for card in soup.select(".gl-item"):
            try:
                title_el = (
                    card.select_one(".p-name a em")
                    or card.select_one(".p-name em")
                    or card.select_one(".p-name-type-2 a")
                )
                img_el = card.select_one(".p-img img")
                price_el = card.select_one(".p-price i") or card.select_one(".p-price strong")
                shop_el = (
                    card.select_one(".p-shop a")
                    or card.select_one(".p-shop span")
                    or card.select_one(".curr-shop")
                )
                link_el = card.select_one("a[href*='item.jd.com']")
                commit_el = card.select_one(".p-commit a") or card.select_one(".p-commit strong")

                title_text = title_el.get_text(strip=True) if title_el else ""
                if not title_text or len(title_text) < 3:
                    continue

                # 图片 src (京东懒加载)
                img_src = ""
                if img_el:
                    img_src = (
                        img_el.get("src")
                        or img_el.get("data-lazy-img")
                        or img_el.get("source-data-lazy-img")
                        or ""
                    )
                    if img_src.startswith("//"):
                        img_src = "https:" + img_src

                # 商品链接
                goods_url = ""
                if link_el:
                    goods_url = link_el.get("href", "")
                    if goods_url.startswith("//"):
                        goods_url = "https:" + goods_url
                    elif goods_url.startswith("/"):
                        goods_url = "https://item.jd.com" + goods_url

                items.append({
                    "goods_name": title_text.replace("【", " ").replace("】", " "),
                    "brand": self._extract_brand(title_text),
                    "model": "",
                    "spec_param": "",
                    "shop_name": shop_el.get_text(strip=True) if shop_el else "",
                    "original_price": self._parse_price(price_el),
                    "real_price": self._parse_price(price_el),
                    "coupon_desc": "",
                    "goods_img": img_src,
                    "goods_url": goods_url,
                    "sales_num": self._parse_jd_commits(commit_el),
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
        """爬取京东商品详情页"""
        print(f"[京东] 正在爬取详情: {link}")
        try:
            html = self._fetch_page(link, wait_selector=".sku-name", wait_ms=3000)
            return self._parse_detail(html, link)
        except Exception as e:
            print(f"[京东] 详情爬取失败: {e}")
            return {}

    def _parse_detail(self, html: str, link: str) -> dict:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")

        title_el = soup.select_one(".sku-name") or soup.select_one(".itemInfo-wrap .sku-name")
        price_el = soup.select_one(".summary-price .price") or soup.select_one(".p-price span")
        img_el = soup.select_one("#spec-img") or soup.select_one(".img-zoom-main img")
        shop_el = soup.select_one(".J-hove-wrap .name a") or soup.select_one(".shop-name")

        title_text = title_el.get_text(strip=True) if title_el else ""

        img_src = ""
        if img_el:
            img_src = img_el.get("src") or img_el.get("data-lazy-img") or ""
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
            "华为", "小米", "Apple", "苹果", "OPPO", "vivo", "三星", "海尔", "美的",
            "格力", "戴尔", "联想", "惠普", "华硕", "荣耀", "索尼", "海信",
            "TCL", "松下", "飞利浦", "西门子", "博世", "小天鹅", "苏泊尔",
            "九阳", "方太", "老板", "科沃斯", "石头", "追觅", "添可",
            "戴森", "SK-II", "兰蔻", "雅诗兰黛", "耐克", "阿迪达斯", "李宁", "安踏",
        ]
        for b in sorted(brands, key=len, reverse=True):
            if b.lower() in title.lower():
                return b
        return ""

    def _parse_jd_commits(self, el) -> int:
        return self._parse_sales(el.get_text(strip=True) if el else "")
