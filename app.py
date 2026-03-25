# app.py
# uvicorn app:app --reload  启动服务命令
#Swagger UI 地址：http://127.0.0.1:8000/docs    
#Swagger JSON 地址：http://127.0.0.1:8000/openapi.json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict

app = FastAPI(title="User Center API")

# 模拟数据库
fake_db: Dict[int, dict] = {}
user_id_seq = 1


class RegisterRequest(BaseModel):
    username: str
    password: str
    email: str


class UpdateRequest(BaseModel):
    user_id: int
    email: str | None = None


@app.post("/user/register")
def register(user: RegisterRequest):
    global user_id_seq

    # 简单重复校验
    for u in fake_db.values():
        if u["username"] == user.username:
            return {"code": 1002, "msg": "用户已存在", "data": None}

    fake_db[user_id_seq] = user.dict()
    fake_db[user_id_seq]["user_id"] = user_id_seq

    user_id_seq += 1

    return {"code": 0, "msg": "success", "data": {"user_id": user_id_seq - 1}}


@app.get("/user/{user_id}")
def get_user(user_id: int):
    if user_id not in fake_db:
        return {"code": 1004, "msg": "用户不存在", "data": None}

    return {"code": 0, "msg": "success", "data": fake_db[user_id]}


@app.put("/user/update")
def update_user(req: UpdateRequest):
    if req.user_id not in fake_db:
        return {"code": 1004, "msg": "用户不存在", "data": None}

    if req.email:
        fake_db[req.user_id]["email"] = req.email

    return {"code": 0, "msg": "success", "data": None}


@app.delete("/user/delete/{user_id}")
def delete_user(user_id: int):
    if user_id not in fake_db:
        return {"code": 1004, "msg": "用户不存在", "data": None}

    del fake_db[user_id]

    return {"code": 0, "msg": "success", "data": None}