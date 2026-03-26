# core/config.py

import os

from dotenv import load_dotenv

load_dotenv()

def _get_bool_env(name: str, default: bool = False) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() in {"1", "true", "yes", "y", "on"}


class Config:
    # 给本地/CI 一个可用的默认值，避免 None 导致 URL 拼接失败
    BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000")
    TOKEN = os.getenv("TOKEN", "")

    # AI（用于自动生成异常场景用例）
    # 说明：deepseek 使用 OpenAI-compatible 接口，Key 来自 DEEPSEEK_API_KEY。
    deepseek_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
    ENABLE_AI_EXCEPTIONS = _get_bool_env("ENABLE_AI_EXCEPTIONS", True)
    AI_MODEL = os.getenv("AI_MODEL", "deepseek-chat")

    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_NAME = os.getenv("DB_NAME")


config = Config()