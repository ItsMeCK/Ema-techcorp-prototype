import os
import logging
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Centralized Configuration Management.
    Loading from .env file or environment variables.
    """
    openai_api_key: str = Field(default="", description="OpenAI API Key for Evaluation Node")
    evaluation_model: str = Field(default="gpt-4o-mini", description="Model used for core reasoning")
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()

# Centralized Logger Configuration
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("EmaResumeService")
