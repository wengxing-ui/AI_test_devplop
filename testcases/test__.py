
import requests
import pytest
from models.user_model import RegisterResponse

def test__(base_url):
    url = f"{base_url}/"
    res = requests.get(url)

    assert res.status_code == 200
    assert res.json()["code"] == 0


def test____get__ai_exc_root_get_001(base_url):
    # GET请求不应包含请求体，但故意发送JSON body
    url = f"{base_url}/"
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


def test____get__ai_exc_root_get_002(base_url):
    # GET请求不应包含请求体，但故意发送空对象body
    url = f"{base_url}/"
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


def test____get__ai_exc_root_get_003(base_url):
    # GET请求不应包含请求体，但故意发送复杂嵌套JSON
    url = f"{base_url}/"
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


def test____get__ai_exc_root_get_004(base_url):
    # GET请求不应包含请求体，但故意发送超长字符串body
    url = f"{base_url}/"
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

