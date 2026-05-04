from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "ProbePilot API"
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    rag_data_dir: str = "data/rag"
    require_human_confirm_high_voltage: bool = True


def get_settings() -> Settings:
    return Settings()
