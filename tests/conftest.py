import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient

# Mocked fixtures for tests since we don't have the full backend implemented in this scope
@pytest.fixture
def anyio_backend():
    return 'asyncio'

@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(base_url="http://test") as client:
        yield client

@pytest.fixture
def auth_token_admin():
    return "mock_admin_token"

@pytest.fixture
def auth_token_viewer():
    return "mock_viewer_token"
