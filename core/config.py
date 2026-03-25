# core/config.py

import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    # 给本地/CI 一个可用的默认值，避免 None 导致 URL 拼接失败
    BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000")
    TOKEN = os.getenv("TOKEN", "")

    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_NAME = os.getenv("DB_NAME")


config = Config()