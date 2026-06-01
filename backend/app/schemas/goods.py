from pydantic import BaseModel


class PriceHistoryPoint(BaseModel):
    date: str
    price: float


class GoodsPriceHistoryResp(BaseModel):
    goods_id: int
    price_history: list[PriceHistoryPoint]
