from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    FARM_NAME: str = "CHEGOLAND AGRI-EMPIRE LTD DAIRY FARM AND SHOP"
    APP_DESCRIPTION: str = "Fresh dairy from our zero-grazing herd in Kapcholyo, Kaplong and its environs"
    FARM_LOCATION: str = "Kapcholyo, Kaplong and its environs"
    DEBUG: bool = True
    SECRET_KEY: str = Field(min_length=32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    COOKIE_SECURE: bool = False
    CORS_ALLOWED_ORIGINS: str = "http://localhost:8000,http://127.0.0.1:8000"
    ALLOWED_HOSTS: str = "localhost,127.0.0.1,testserver"

    # Database
    DATABASE_URL: str = "sqlite:///./dairy_farm.db"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # M-Pesa Daraja
    MPESA_ENVIRONMENT: str = "sandbox"
    MPESA_CONSUMER_KEY: Optional[str] = None
    MPESA_CONSUMER_SECRET: Optional[str] = None
    MPESA_BUSINESS_SHORT_CODE: str = "174379"
    MPESA_PASSKEY: Optional[str] = None
    MPESA_CALLBACK_URL: Optional[str] = None
    MPESA_MOCK_MODE: bool = True

    # Email / SMTP
    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM: str = "noreply@chegoland.com"

    # Africa's Talking SMS
    AT_USERNAME: Optional[str] = None
    AT_API_KEY: Optional[str] = None
    AT_SENDER_ID: Optional[str] = None

    # Admin credentials (seeded on first run)
    ADMIN_EMAIL: str = "admin@chegoland.com"
    ADMIN_PASSWORD: str

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ALLOWED_ORIGINS.split(",") if origin.strip()]

    @property
    def allowed_hosts(self) -> list[str]:
        return [host.strip() for host in self.ALLOWED_HOSTS.split(",") if host.strip()]

    @property
    def APP_NAME(self) -> str:
        return self.FARM_NAME


settings = Settings()