from pydantic import BaseModel, Field, HttpUrl


class UrlCompareReq(BaseModel):
    goods_url: HttpUrl = Field(..., description="商品链接")
    token: str | None = Field(default=None)


class SearchCompareReq(BaseModel):
    keyword: str = Field(..., min_length=1, max_length=255, description="商品名称、品牌或型号")
    token: str | None = Field(default=None)


class CompareResultItem(BaseModel):
    goods_id: int
    goods_name: str
    brand: str
    model: str
    spec_param: str
    platform: str
    shop_name: str
    original_price: float
    real_price: float
    coupon_desc: str
    goods_img: str
    goods_url: str
    sales_num: int
    score: float
    sale_status: int
    match_score: float = 0
    trust_score: float = 0


class PricePoint(BaseModel):
    goods_id: int = 0
    date: str
    price: float


class AIAnalysis(BaseModel):
    price_level: str
    buy_advice: str
    price_prediction: str


class CompareResultResp(BaseModel):
    goods_info: str
    ai_analysis: AIAnalysis
    price_history: list[PricePoint]
    compare_list: list[CompareResultItem]
