from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal

class Settings(BaseSettings):

    GEMINI_API_KEY: str | None = None
    DEEPSEEK_API_KEY: str | None = None
    GIGACHAT_CREDENTIALS: str | None = None
    TELEGRAM_BOT_TOKEN: str | None = None
    
    EMBEDDING_MODEL: str = "BAAI/bge-m3"
    VECTOR_DB_PATH: str = "data/vector_db"

    LLM_PROVIDER: Literal["gigachat", "qwen"] = "gigachat"

    QWEN_BASE_URL: str = "http://127.0.0.1:8080/v1"
    QWEN_MODEL: str = "Qwen3-1.7B-Q4_K_M"
    QWEN_TEMPERATURE: float = 0.2
    QWEN_MAX_TOKENS: int = 500
      
    CHUNK_SIZE: int = 700
    CHUNK_OVERLAP: int = 150

    TOP_K: int = 3

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
