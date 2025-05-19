import asyncio
import pytest

@pytest.mark.asyncio
async def test_jopa() -> None:
    await asyncio.sleep(1)
    assert True
