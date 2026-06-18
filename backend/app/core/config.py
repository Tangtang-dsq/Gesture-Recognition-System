from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).resolve().parents[3]
BACKEND_DIR = ROOT_DIR / "backend"
DATA_DIR = ROOT_DIR / "data"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT_DIR / ".env", extra="ignore")

    database_url: str = "postgresql+psycopg://gesture:gesture@localhost:5432/gesture"
    redis_url: str = "redis://localhost:6379/0"
    dataset_root: Path = DATA_DIR
    allowed_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    conf_threshold: float = 0.65
    vote_n: int = 5
    vote_min: int = 3
    cooldown_seconds: float = 0.8
    seq_len: int = 30
    static_model_path: Path = BACKEND_DIR / "app" / "models" / "static_classifier.joblib"
    dynamic_model_path: Path = BACKEND_DIR / "app" / "models" / "dynamic_classifier.joblib"
    static_labels: tuple[str, ...] = (
        "fist",
        "palm",
        "peace",
        "point",
        "thumbs_up",
        "ok",
        "number_1",
        "number_2",
        "number_3",
        "number_4",
        "number_5",
    )
    dynamic_labels: tuple[str, ...] = (
        "none",
        "swipe_left",
        "swipe_right",
        "swipe_up",
        "swipe_down",
        "zoom_in",
        "zoom_out",
    )

    @property
    def allowed_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
