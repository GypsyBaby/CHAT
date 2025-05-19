import pytest

from src.settings import settings

from src.database.postgresql.connection import create_engine, SessionFactory, SessionWrapper, AsyncSession



@pytest.fixture
def async_session_wrapper() -> SessionWrapper:
    engine = create_engine(settings.DATABASE_ASYNC_URL)
    asf = SessionFactory(engine)
    asw = SessionWrapper(asf)
    return asw
