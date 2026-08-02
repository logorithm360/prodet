from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Business OS"
    environment: str = "development"
    debug: bool = True

    database_url: str = "postgresql://user:password@localhost:5432/business_os"
    secret_key: str = "change-me-in-production"

    class Config:
        env_file = ".env"

settings = Settings()