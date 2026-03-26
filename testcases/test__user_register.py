
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


def test__user_register__post__ai_exc_user_register_missing_username(base_url):
    # 缺失必填字段 username
    url = f"{base_url}/user/register"
    payload = {'password': 'validPass123', 'email': 'test@example.com'}
    res = requests.post(url, json=payload)

    assert res.status_code == 422
    from typing import Any
    from pydantic import BaseModel

    class _ApiResponse(BaseModel):
        code: int | None = None
        msg: str | None = None
        data: Any = None
        detail: Any = None

    resp_json = res.json()
    _validated = _ApiResponse.model_validate(resp_json)
    # expected_business_code 为 null：不对 code 做精确断言


def test__user_register__post__ai_exc_user_register_missing_password(base_url):
    # 缺失必填字段 password
    url = f"{base_url}/user/register"
    payload = {'username': 'testuser', 'email': 'test@example.com'}
    res = requests.post(url, json=payload)

    assert res.status_code == 422
    from typing import Any
    from pydantic import BaseModel

    class _ApiResponse(BaseModel):
        code: int | None = None
        msg: str | None = None
        data: Any = None
        detail: Any = None

    resp_json = res.json()
    _validated = _ApiResponse.model_validate(resp_json)
    # expected_business_code 为 null：不对 code 做精确断言


def test__user_register__post__ai_exc_user_register_missing_email(base_url):
    # 缺失必填字段 email
    url = f"{base_url}/user/register"
    payload = {'username': 'testuser', 'password': 'validPass123'}
    res = requests.post(url, json=payload)

    assert res.status_code == 422
    from typing import Any
    from pydantic import BaseModel

    class _ApiResponse(BaseModel):
        code: int | None = None
        msg: str | None = None
        data: Any = None
        detail: Any = None

    resp_json = res.json()
    _validated = _ApiResponse.model_validate(resp_json)
    # expected_business_code 为 null：不对 code 做精确断言


def test__user_register__post__ai_exc_user_register_username_type_error(base_url):
    # username 字段类型错误（传整数）
    url = f"{base_url}/user/register"
    payload = {'username': 12345, 'password': 'validPass123', 'email': 'test@example.com'}
    res = requests.post(url, json=payload)

    assert res.status_code == 422
    from typing import Any
    from pydantic import BaseModel

    class _ApiResponse(BaseModel):
        code: int | None = None
        msg: str | None = None
        data: Any = None
        detail: Any = None

    resp_json = res.json()
    _validated = _ApiResponse.model_validate(resp_json)
    # expected_business_code 为 null：不对 code 做精确断言


def test__user_register__post__ai_exc_user_register_password_type_error(base_url):
    # password 字段类型错误（传布尔值）
    url = f"{base_url}/user/register"
    payload = {'username': 'testuser', 'password': True, 'email': 'test@example.com'}
    res = requests.post(url, json=payload)

    assert res.status_code == 422
    from typing import Any
    from pydantic import BaseModel

    class _ApiResponse(BaseModel):
        code: int | None = None
        msg: str | None = None
        data: Any = None
        detail: Any = None

    resp_json = res.json()
    _validated = _ApiResponse.model_validate(resp_json)
    # expected_business_code 为 null：不对 code 做精确断言


def test__user_register__post__ai_exc_user_register_username_too_long(base_url):
    # username 超长（超过20字符）
    url = f"{base_url}/user/register"
    payload = {'username': 'thisusernameiswaytoolongfortheschema', 'password': 'validPass123', 'email': 'test@example.com'}
    res = requests.post(url, json=payload)

    assert res.status_code == 422
    from typing import Any
    from pydantic import BaseModel

    class _ApiResponse(BaseModel):
        code: int | None = None
        msg: str | None = None
        data: Any = None
        detail: Any = None

    resp_json = res.json()
    _validated = _ApiResponse.model_validate(resp_json)
    # expected_business_code 为 null：不对 code 做精确断言


def test__user_register__post__ai_exc_user_register_password_too_long(base_url):
    # password 超长（超过30字符）
    url = f"{base_url}/user/register"
    payload = {'username': 'testuser', 'password': 'thispasswordiswaytoolongandexceedsthemaxlengthof30characters', 'email': 'test@example.com'}
    res = requests.post(url, json=payload)

    assert res.status_code == 422
    from typing import Any
    from pydantic import BaseModel

    class _ApiResponse(BaseModel):
        code: int | None = None
        msg: str | None = None
        data: Any = None
        detail: Any = None

    resp_json = res.json()
    _validated = _ApiResponse.model_validate(resp_json)
    # expected_business_code 为 null：不对 code 做精确断言


def test__user_register__post__ai_exc_user_register_invalid_email_format(base_url):
    # email 格式非法（不符合email格式）
    url = f"{base_url}/user/register"
    payload = {'username': 'testuser', 'password': 'validPass123', 'email': 'not-an-email'}
    res = requests.post(url, json=payload)

    assert res.status_code == 422
    from typing import Any
    from pydantic import BaseModel

    class _ApiResponse(BaseModel):
        code: int | None = None
        msg: str | None = None
        data: Any = None
        detail: Any = None

    resp_json = res.json()
    _validated = _ApiResponse.model_validate(resp_json)
    # expected_business_code 为 null：不对 code 做精确断言

