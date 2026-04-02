from typing import List, Optional
from pydantic import BaseModel


# --- Geo / Search ---

class GeoResult(BaseModel):
    name: str
    country: str
    state: Optional[str] = None
    lat: float
    lon: float


# --- Current Weather ---

class WeatherCondition(BaseModel):
    id: int
    main: str
    description: str
    icon: str
    icon_url: str


class WindInfo(BaseModel):
    speed: float
    deg: int
    gust: Optional[float] = None


class MainMetrics(BaseModel):
    temp: float
    feels_like: float
    temp_min: float
    temp_max: float
    pressure: int
    humidity: int


class SysInfo(BaseModel):
    sunrise: int
    sunset: int
    country: str


class CurrentWeatherResponse(BaseModel):
    city: str
    country: str
    lat: float
    lon: float
    timezone_offset: int
    dt: int
    weather: WeatherCondition
    main: MainMetrics
    wind: WindInfo
    visibility: Optional[int] = None
    clouds: int
    units: str
    cached: bool = False


# --- Forecast ---

class ForecastItem(BaseModel):
    dt: int
    dt_txt: str
    weather: WeatherCondition
    main: MainMetrics
    wind: WindInfo
    clouds: int
    pop: float   # probability of precipitation


class ForecastResponse(BaseModel):
    city: str
    country: str
    lat: float
    lon: float
    units: str
    forecast: List[ForecastItem]
    cached: bool = False
