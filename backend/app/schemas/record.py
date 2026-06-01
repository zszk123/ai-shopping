from pydantic import BaseModel, Field


class CompareRecordItem(BaseModel):
    id: int
    search_source: str
    compare_type: int  # 1图片 2链接 3关键词
    create_time: str

    class Config:
        from_attributes = True


class DeleteRecordReq(BaseModel):
    record_id: int = Field(...)
