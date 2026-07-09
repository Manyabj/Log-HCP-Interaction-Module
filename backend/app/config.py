"""
Central application configuration.
Loads values from environment variables / .env file.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg2://postgres:5002@localhost:5432/hcp_crm"

    groq_api_key: str = "your_api_key_here"
    groq_chat_model: str = "llama-3.3-70b-versatile"
    groq_reasoning_model: str = "llama-3.3-70b-versatile"

    frontend_origin: str = "http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
