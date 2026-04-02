from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    OPENWEATHER_API_KEY: str = "your_api_key_here"
    OPENWEATHER_BASE_URL: str = "https://api.openweathermap.org/data/2.5"
    OPENWEATHER_GEO_URL: str = "http://api.openweathermap.org/geo/1.0"

    REDIS_URL: str = "redis://localhost:6379"
    CACHE_TTL_CURRENT: int = 600       # 10 minutes for current weather
    CACHE_TTL_FORECAST: int = 1800     # 30 minutes for forecast
    CACHE_TTL_SEARCH: int = 86400      # 24 hours for geocoding

    DEFAULT_UNITS: str = "metric"      # metric | imperial | standard

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
