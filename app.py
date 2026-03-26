# app.py
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, Dict, Any
import uuid
import re

app = FastAPI(title="Test API", version="1.0.0")

# 模拟数据库（内存存储）
users_db: Dict[str, dict] = {}

# ----- 请求/响应模型 -----
class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=20, description="用户名，3-20个字符")
    password: str = Field(..., min_length=6, max_length=30, description="密码，6-30个字符")
    email: EmailStr = Field(..., description="邮箱地址")

    @validator('username')
    def username_alphanumeric(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('用户名只能包含字母、数字和下划线')
        return v

class UserRegisterResponse(BaseModel):
    user_id: str
    username: str
    email: str

class StandardResponse(BaseModel):
    code: int = 0
    msg: str = "success"
    data: Optional[Any] = None

class ErrorResponse(BaseModel):
    code: int
    msg: str

# ----- 接口实现 -----
@app.post(
    "/user/register",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "请求参数错误"},
        409: {"model": ErrorResponse, "description": "用户名或邮箱已存在"},
    }
)
async def register(user: UserRegisterRequest):
    """
    用户注册接口

    - **username**: 用户名，3-20个字符，只能包含字母、数字和下划线
    - **password**: 密码，6-30个字符
    - **email**: 有效的邮箱地址
    """
    # 检查用户名是否已存在
    for u in users_db.values():
        if u["username"] == user.username:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"code": 1001, "msg": "用户名已存在"}
            )
        if u["email"] == user.email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"code": 1002, "msg": "邮箱已被注册"}
            )

    # 生成用户ID
    user_id = str(uuid.uuid4())
    users_db[user_id] = {
        "user_id": user_id,
        "username": user.username,
        "email": user.email,
        "password": user.password  # 实际项目中应哈希存储
    }

    # 返回响应
    return StandardResponse(
        data=UserRegisterResponse(
            user_id=user_id,
            username=user.username,
            email=user.email
        )
    )

@app.get(
    "/user/{user_id}",
    response_model=StandardResponse,
    responses={
        404: {"model": ErrorResponse, "description": "用户不存在"}
    }
)
async def get_user(user_id: str):
    """
    获取用户信息

    - **user_id**: 用户唯一标识
    """
    user = users_db.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": 1003, "msg": "用户不存在"}
        )
    return StandardResponse(
        data={
            "user_id": user["user_id"],
            "username": user["username"],
            "email": user["email"]
        }
    )

# 可选：添加根路径，便于健康检查
@app.get("/")
async def root():
    return {"message": "API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)