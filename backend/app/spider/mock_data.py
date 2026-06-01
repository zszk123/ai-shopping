"""模拟商品数据生成器 - Selenium/Edge无法正常抓取时的兜底数据"""
import hashlib
import random

# 各平台常见店铺名
SHOP_NAMES = {
    "淘宝": ["天猫官方旗舰店", "XX数码专营店", "YY电器旗舰店", "品牌授权店", "省心购旗舰店",
             "品质数码店", "官方直营店", "优选数码店", "正品保障店", "品牌折扣店"],
    "京东": ["京东自营旗舰店", "品牌京东自营店", "XX数码京东自营", "YY官方旗舰店",
             "京东国际自营", "品牌授权专卖店", "京东之家", "京东电器旗舰店", "京东全球购", "京东官方店"],
    "拼多多": ["百亿补贴官方", "品牌折扣店", "好货精选店", "省新优选", "品牌特卖店",
             "品质优选店", "官方授权店", "超级省心购", "品牌专卖店", "实惠数码店"],
    "抖音": ["官方旗舰店", "XX品牌直播间", "数码精选店", "品质好物店", "品牌正品店",
             "爆品推荐店", "品牌直销店", "优选数码店", "品牌官旗直播", "好物推荐官"],
}

# 热门商品模板（带型号/规格变体）
PRODUCT_TEMPLATES = {
    "iphone": {
        "names": [
            "Apple iPhone 16 Pro Max {storage} {color} 5G全网通",
            "iPhone 16 Pro Max {storage} {color} 国行原封",
            "苹果 iPhone 16 Pro Max {storage} {color} 全新正品",
        ],
        "storage": ["256GB", "512GB", "1TB"],
        "color": ["黑色钛金属", "白色钛金属", "原色钛金属", "沙漠钛金属"],
        "brand": "Apple",
        "base_price": (8299, 12999),
    },
    "huawei": {
        "names": [
            "华为 Mate 70 Pro+ {storage} {color} 5G智能手机",
            "HUAWEI Mate 70 Pro+ {storage} {color} 鸿蒙OS",
            "华为 Mate 70 Pro+ {storage} {color} 卫星通信版",
        ],
        "storage": ["256GB", "512GB", "1TB"],
        "color": ["曜金黑", "青山黛", "云杉绿", "雪域白"],
        "brand": "华为",
        "base_price": (6999, 10999),
    },
    "xiaomi": {
        "names": [
            "小米15 Ultra {storage} {color} 骁龙8至尊版",
            "Xiaomi 15 Ultra {storage} {color} 徕卡光学",
            "小米 15 Ultra {storage} {color} 5G旗舰手机",
        ],
        "storage": ["12+256GB", "16+512GB", "16+1TB"],
        "color": ["黑色", "白色", "橄榄绿"],
        "brand": "小米",
        "base_price": (4999, 7999),
    },
    "macbook": {
        "names": [
            "Apple MacBook Pro 14英寸 {chip} {storage} 深空黑色",
            "MacBook Pro 14\" {chip} {storage} 2024款",
            "苹果 MacBook Pro 14 {chip} {storage} 正品国行",
        ],
        "storage": ["512GB", "1TB", "2TB"],
        "chip": ["M4", "M4 Pro", "M4 Max"],
        "brand": "Apple",
        "base_price": (12999, 26999),
    },
    "nike": {
        "names": [
            "Nike {series} {color} 男/女运动鞋",
            "耐克 {series} {color} 缓震跑步鞋",
            "Nike {series} {color} 空军一号板鞋",
        ],
        "series": ["Air Max 270", "Air Force 1", "React Pegasus", "Dunk Low", "Vapormax"],
        "color": ["黑白", "纯白", "灰蓝", "黑红", "蓝白"],
        "brand": "耐克",
        "base_price": (299, 1299),
    },
    "default": {
        "names": [
            "{keyword} {spec} {color} 热销爆款",
            "{keyword} {spec} {color} 正品保障",
            "【正品】{keyword} {spec} {color} 全国联保",
        ],
        "spec": ["旗舰版", "标准版", "升级版", "Pro版", ""],
        "color": ["黑色", "白色", "灰色", "蓝色", ""],
        "brand": "",
        "base_price": (50, 5000),
    },
}

# 平台折扣系数（拼多多最便宜，京东最接近标价）
PLATFORM_DISCOUNT = {
    "淘宝": (0.85, 0.98),
    "京东": (0.92, 1.0),
    "拼多多": (0.65, 0.92),
    "抖音": (0.80, 0.97),
}

# 各平台优惠券文案模板
COUPON_TEMPLATES = {
    "淘宝": ["满{0}减{1}", "跨店每{0}减{1}", "店铺券{0}元", ""],
    "京东": ["PLUS会员{0}元券", "满{0}减{1}", "白条{0}期免息", ""],
    "拼多多": ["百亿补贴{0}元券", "满{0}减{1}", "品牌限时补贴", "领券再减{0}元", ""],
    "抖音": ["新人{0}元券", "直播间专属价", "限时秒杀", ""],
}


def _pick_template(keyword: str) -> dict:
    kw_lower = keyword.lower()
    for k in PRODUCT_TEMPLATES:
        if k in kw_lower:
            return PRODUCT_TEMPLATES[k]
    return PRODUCT_TEMPLATES["default"]


def _gen_name(tmpl: dict, keyword: str) -> str:
    pattern = random.choice(tmpl["names"])
    result = pattern.format(
        storage=random.choice(tmpl.get("storage", [""])),
        color=random.choice(tmpl.get("color", [""])),
        chip=random.choice(tmpl.get("chip", [""])),
        series=random.choice(tmpl.get("series", [""])),
        spec=random.choice(tmpl.get("spec", [""])),
        keyword=keyword,
    )
    # 清理多余空格
    import re
    return re.sub(r"\s+", " ", result).strip()


def _gen_coupon(platform: str, price: float) -> str:
    templates = COUPON_TEMPLATES.get(platform, [])
    tpl = random.choice(templates)
    if not tpl:
        return ""
    if "{0}" in tpl and "{1}" in tpl:
        coupon = max(int(price * 0.03), 5)
        discount = max(coupon * 2, 30)
        return tpl.format(coupon, discount)
    elif "{0}" in tpl:
        return tpl.format(random.choice([5, 10, 15, 20, 30, 50]))
    return tpl


def generate_mock_goods(keyword: str, platform: str, count: int = 8) -> list[dict]:
    """生成模拟商品数据"""
    tmpl = _pick_template(keyword)
    brand = tmpl.get("brand", keyword)
    price_min, price_max = tmpl.get("base_price", (50, 5000))
    discount_min, discount_max = PLATFORM_DISCOUNT.get(platform, (0.8, 1.0))
    shops = SHOP_NAMES.get(platform, [])

    goods_list = []
    for i in range(count):
        original = round(random.uniform(price_min, price_max), 2)
        discount = random.uniform(discount_min, discount_max)
        real_price = round(original * discount, 2)
        name = _gen_name(tmpl, keyword)
        goods_id_hash = hashlib.md5(f"{platform}:{name}:{i}".encode()).hexdigest()[:12]

        goods_list.append({
            "goods_name": name,
            "brand": brand,
            "model": "",
            "spec_param": "",
            "platform": platform,
            "shop_name": random.choice(shops) if shops else "",
            "original_price": original,
            "real_price": real_price,
            "coupon_desc": _gen_coupon(platform, real_price),
            "goods_img": "",
            "goods_url": f"https://mock.example.com/{platform}/{goods_id_hash}",
            "sales_num": random.randint(0, 50000) if random.random() > 0.2 else 0,
            "score": round(random.uniform(4.0, 5.0), 1),
            "sale_status": random.choice([1, 1, 1, 1, 0]),
        })
    return goods_list
