# API Contract

All business APIs return the same envelope:

```json
{
  "code": 200,
  "msg": "ok",
  "data": {}
}
```

Frontend should treat `code != 200` as a business failure, even when HTTP status is 200.

## Auth

### POST `/api/user/register`

Request:

```json
{
  "username": "demo",
  "password": "123456",
  "phone": "13800138000"
}
```

Data:

```json
{
  "token": "jwt-token",
  "user_id": 1
}
```

### POST `/api/user/login`

Request:

```json
{
  "phone": "13800138000",
  "password": "123456"
}
```

Data is the same as register.

## Compare

### POST `/api/compare/image`

Multipart form field:

- `file`: jpg, png or webp image, max 8MB.

Data:

```json
{
  "goods_info": "recognized product query",
  "extracted_info": {
    "goods_name": "商品名称",
    "brand": "品牌",
    "model": "型号",
    "price": "图片中出现的价格",
    "category": "类目",
    "specs": "规格参数"
  },
  "ai_analysis": {
    "price_level": "适中",
    "buy_advice": "购买建议",
    "price_prediction": "趋势判断"
  },
  "price_history": [],
  "compare_list": []
}
```

### POST `/api/compare/url`

Request:

```json
{
  "goods_url": "https://item.jd.com/xxx.html"
}
```

### GET `/api/compare/search?keyword=iPhone`

Searches by keyword and returns the same data shape as image compare, except `extracted_info` may be absent.

## Internal APIs

Routes under `/api/internal/*` and `/api/spider/*` require:

```text
X-Internal-Token: <INTERNAL_API_TOKEN>
```

## Generated Contract

FastAPI also exposes machine-readable OpenAPI at:

```text
http://127.0.0.1:8000/openapi.json
```

The Flutter client should keep model parsing aligned with this contract.
