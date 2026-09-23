import os
from pathlib import Path


class Settings:
    PROJECT_NAME: str = "NMDC Bailadila Safety Control Room"
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY", "NMDC_SECURE_INDUSTRIAL_SECRET_KEY_987654321"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 hours operator shift

    BASE_DIR: Path = Path(__file__).resolve().parent
    DATABASE_DIR: Path = BASE_DIR / "database"
    DATABASE_DIR.mkdir(exist_ok=True)
    DATABASE_FILE: Path = DATABASE_DIR / "safety_system.db"
    DATABASE_URL: str = f"sqlite:///{DATABASE_FILE.resolve().as_posix()}"


settings = Settings()
