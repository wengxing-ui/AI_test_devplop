# models/user_model.py

from pydantic import BaseModel


class RegisterResponse(BaseModel):  # 注册响应模型
    code: int
    msg: str
    data: dict | None