
import requests
import pytest
import time
from models.user_model import RegisterResponse

def test__user_register(base_url):
    unique = str(int(time.time() * 1000))
    url = f"{base_url}/user/register"

    payload = { "username": f"test1_{unique}", "password": "123456", "email": f"test{unique}@test.com" }
    res = requests.post(url, json=payload)

    assert res.status_code == 200
    assert res.json()["code"] == 0
