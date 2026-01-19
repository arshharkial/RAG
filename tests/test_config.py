from src.core.config import settings

def test_settings_load():
    assert settings.ALGORITHM == "HS256"
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 30

def test_db_url_format():
    assert settings.DATABASE_URL.startswith("postgresql+asyncpg://")
