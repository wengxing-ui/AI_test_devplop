import pytest

from core.config import config


@pytest.fixture(scope="session")
def base_url():
    return config.BASE_URL


@pytest.fixture(scope="session")
def auth_token():
    return config.TOKEN
