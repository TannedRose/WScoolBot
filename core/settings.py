from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        frozen=True,
        case_sensitive=False,
        extra="allow",
        env_file=".env",
        env_file_encoding="utf-8",
    )
    BOT_TOKEN: str
    PG_URL: str

settings = Settings()
