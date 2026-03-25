
import requests
import pytest
import time
from models.user_model import RegisterResponse

def test__user_delete_user_id(base_url):
    unique = str(int(time.time() * 1000))

    register_url = f"{base_url}/user/register"
    register_payload = { "username": f"test1_{unique}", "password": "123456", "email": f"test{unique}@test.com" }
    register_res = requests.post(register_url, json=register_payload)
    assert register_res.status_code == 200
    assert register_res.json()["code"] == 0
    user_id = register_res.json()["data"]["user_id"]
    url = f"{base_url}/user/delete/{user_id}"
    res = requests.delete(url)

    assert res.status_code == 200
    assert res.json()["code"] == 0
