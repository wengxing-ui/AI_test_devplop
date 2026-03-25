# testcases/test_user.py

import requests
import pytest


def test_register(base_url):
    url = f"{base_url}/user/register"

    payload = {
        "username": "test1",
        "password": "123456",
        "email": "test@test.com"
    }

    res = requests.post(url, json=payload)

    assert res.status_code == 200
    assert res.json()["code"] == 0