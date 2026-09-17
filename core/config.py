from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    service_name: str = "sigma-m-verification-python"
    environment: str = "dev"

    api_key: str = "Clave_asi_super_secreta_cambiar_en_producción"

    max_upload: int = 8 * 1024 * 1024
    allowed_content_types: tuple[str,...] = ("image/jpg", "image/png")

    face_model: str = "buffalo_1"
    face_size: int = 640

    face_match: float = 0.48

    ocr: str = "apa"

    log: str = "INFO"

@lru_cache
def get_settings() -> Settings:
    return Settings()