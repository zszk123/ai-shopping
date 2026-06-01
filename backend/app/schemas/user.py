from pydantic import BaseModel, Field


class UserRegisterReq(BaseModel):
    username: str = Field(..., min_length=1, max_length=32)
    password: str = Field(..., min_length=6, max_length=64)
    phone: str = Field(..., min_length=11, max_length=11, pattern=r"^\d{11}$")


class UserLoginReq(BaseModel):
    phone: str = Field(..., min_length=11, max_length=11, pattern=r"^\d{11}$")
    password: str = Field(..., min_length=6, max_length=64)


class UserUpdateReq(BaseModel):
    username: str | None = Field(default=None, max_length=32)
    avatar: str | None = Field(default=None, max_length=512)


class UserInfoResp(BaseModel):
    id: int
    username: str
    phone: str
    avatar: str
    status: int
    create_time: str

    class Config:
        from_attributes = True
