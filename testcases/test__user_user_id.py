
import requests
import pytest
import time
from models.user_model import RegisterResponse

def test__user_user_id(base_url):
    unique = str(int(time.time() * 1000))

    register_url = f"{base_url}/user/register"
    register_payload = { "username": f"test1_{unique}", "password": "123456", "email": f"test{unique}@test.com" }
    register_res = requests.post(register_url, json=register_payload)
    assert register_res.status_code == 200
    assert register_res.json()["code"] == 0
    user_id = register_res.json()["data"]["user_id"]
    url = f"{base_url}/user/{user_id}"
    res = requests.get(url)

    assert res.status_code == 200
    assert res.json()["code"] == 0


def test__user_user_id__get__ai_exc_get_user_path_var_type_error_string_to_int(base_url):
    # 路径参数 user_id 类型错误：传入字符串而非整数
    user_id = 'not_a_number'
    url = f"{base_url}/user/{user_id}"
    res = requests.get(url)

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


def test__user_user_id__get__ai_exc_get_user_path_var_negative_integer(base_url):
    # 路径参数 user_id 为负数，触发资源不存在类业务异常
    user_id = -999
    url = f"{base_url}/user/{user_id}"
    res = requests.get(url)

    assert res.status_code == 404
    from typing import Any
    from pydantic import BaseModel

    class _ApiResponse(BaseModel):
        code: int | None = None
        msg: str | None = None
        data: Any = None
        detail: Any = None

    resp_json = res.json()
    _validated = _ApiResponse.model_validate(resp_json)
    if _validated.code is None:
        raise AssertionError('响应缺少 code 字段，无法断言 expected_business_code')
    assert _validated.code == 404


def test__user_user_id__get__ai_exc_get_user_path_var_zero(base_url):
    # 路径参数 user_id 为0，可能触发资源不存在或无效ID类业务异常
    user_id = 0
    url = f"{base_url}/user/{user_id}"
    res = requests.get(url)

    assert res.status_code == 404
    from typing import Any
    from pydantic import BaseModel

    class _ApiResponse(BaseModel):
        code: int | None = None
        msg: str | None = None
        data: Any = None
        detail: Any = None

    resp_json = res.json()
    _validated = _ApiResponse.model_validate(resp_json)
    if _validated.code is None:
        raise AssertionError('响应缺少 code 字段，无法断言 expected_business_code')
    assert _validated.code == 404


def test__user_user_id__get__ai_exc_get_user_path_var_very_large_number(base_url):
    # 路径参数 user_id 为非常大的整数，触发资源不存在类业务异常
    user_id = 999999999999999999
    url = f"{base_url}/user/{user_id}"
    res = requests.get(url)

    assert res.status_code == 404
    from typing import Any
    from pydantic import BaseModel

    class _ApiResponse(BaseModel):
        code: int | None = None
        msg: str | None = None
        data: Any = None
        detail: Any = None

    resp_json = res.json()
    _validated = _ApiResponse.model_validate(resp_json)
    if _validated.code is None:
        raise AssertionError('响应缺少 code 字段，无法断言 expected_business_code')
    assert _validated.code == 404


def test__user_user_id__get__ai_exc_get_user_path_var_empty_string(base_url):
    # 路径参数 user_id 为空字符串，类型错误
    user_id = ''
    url = f"{base_url}/user/{user_id}"
    res = requests.get(url)

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


def test__user_user_id__get__ai_exc_get_user_path_var_special_chars(base_url):
    # 路径参数 user_id 包含特殊字符，类型错误
    user_id = '123@abc'
    url = f"{base_url}/user/{user_id}"
    res = requests.get(url)

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


def test__user_user_id__get__ai_exc_get_user_path_var_float_number(base_url):
    # 路径参数 user_id 为浮点数，类型错误
    user_id = 123.45
    url = f"{base_url}/user/{user_id}"
    res = requests.get(url)

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

