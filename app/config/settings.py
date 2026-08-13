from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    GEMINI_API_KEY: str | None = None
    DEEPSEEK_API_KEY: str | None = None
    GIGACHAT_CREDENTIALS: str | None = None

    EMBEDDING_MODEL: str = "BAAI/bge-m3"

    VECTOR_DB_PATH: str = "data/vector_db"

    CHUNK_SIZE: int = 700
    CHUNK_OVERLAP: int = 150

    TOP_K: int = 3

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()