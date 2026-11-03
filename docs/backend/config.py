import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "AgriVision AI AgTech System"
    APP_ENV: str = "development"
    SECRET_KEY: str = "agrivision-secret-key-change-in-production"
    
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Serial / Hardware
    SERIAL_PORT: str = "COM3"
    SERIAL_BAUD_RATE: int = 9600
    SERIAL_TIMEOUT: float = 2.0
    
    # Operating Mode
    DEMO_MODE: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite:///./agrivision.db"
    
    # Weather
    WEATHER_API_KEY: str = ""
    WEATHER_CITY: str = "Sacramento"
    WEATHER_LAT: float = 38.5816
    WEATHER_LON: float = -121.4944
    
    # Defaults
    DEFAULT_MOISTURE_THRESHOLD: float = 35.0
    DEFAULT_TEMP_MAX: float = 35.0
    DEFAULT_PH_MIN: float = 6.0
    DEFAULT_PH_MAX: float = 7.5
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
