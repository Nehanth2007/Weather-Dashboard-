import logging
from typing import List, Optional

import httpx

from app.core.config import settings
from app.core.cache import get_cached, set_cached
from app.models.weather import (
    CurrentWeatherResponse,
    ForecastResponse,
    ForecastItem,
    GeoResult,
    WeatherCondition,
    WindInfo,
    MainMetrics,
    SysInfo,
)

logger = logging.getLogger(__name__)

ICON_URL = "https://openweathermap.org/img/wn/{}@2x.png"


def _parse_condition(w: dict) -> WeatherCondition:
    return WeatherCondition(
        id=w["id"],
        main=w["main"],
        description=w["description"],
        icon=w["icon"],
        icon_url=ICON_URL.format(w["icon"]),
    )


def _parse_main(m: dict) -> MainMetrics:
    return MainMetrics(
        temp=m["temp"],
        feels_like=m["feels_like"],
        temp_min=m["temp_min"],
        temp_max=m["temp_max"],
        pressure=m["pressure"],
        humidity=m["humidity"],
    )


def _parse_wind(w: dict) -> WindInfo:
    return WindInfo(
        speed=w.get("speed", 0),
        deg=w.get("deg", 0),
        gust=w.get("gust"),
    )


async def geocode(city: str) -> List[GeoResult]:
    """Convert city name to lat/lon using OWM Geocoding API."""
    cache_key = f"geo:{city.lower().strip()}"
    cached = await get_cached(cache_key)
    if cached:
        return [GeoResult(**item) for item in cached]

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            f"{settings.OPENWEATHER_GEO_URL}/direct",
            params={
                "q": city,
                "limit": 5,
                "appid": settings.OPENWEATHER_API_KEY,
            },
        )
        resp.raise_for_status()
        data = resp.json()

    results = [
        GeoResult(
            name=item["name"],
            country=item["country"],
            state=item.get("state"),
            lat=item["lat"],
            lon=item["lon"],
        )
        for item in data
    ]

    await set_cached(cache_key, [r.model_dump() for r in results], settings.CACHE_TTL_SEARCH)
    return results


async def get_current_weather(
    lat: float,
    lon: float,
    units: str = settings.DEFAULT_UNITS,
) -> CurrentWeatherResponse:
    cache_key = f"current:{lat:.4f}:{lon:.4f}:{units}"
    cached = await get_cached(cache_key)
    if cached:
        return CurrentWeatherResponse(**{**cached, "cached": True})

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            f"{settings.OPENWEATHER_BASE_URL}/weather",
            params={
                "lat": lat,
                "lon": lon,
                "units": units,
                "appid": settings.OPENWEATHER_API_KEY,
            },
        )
        resp.raise_for_status()
        data = resp.json()

    result = CurrentWeatherResponse(
        city=data["name"],
        country=data["sys"]["country"],
        lat=data["coord"]["lat"],
        lon=data["coord"]["lon"],
        timezone_offset=data["timezone"],
        dt=data["dt"],
        weather=_parse_condition(data["weather"][0]),
        main=_parse_main(data["main"]),
        wind=_parse_wind(data.get("wind", {})),
        visibility=data.get("visibility"),
        clouds=data["clouds"]["all"],
        units=units,
        cached=False,
    )

    await set_cached(cache_key, result.model_dump(), settings.CACHE_TTL_CURRENT)
    return result


async def get_forecast(
    lat: float,
    lon: float,
    units: str = settings.DEFAULT_UNITS,
) -> ForecastResponse:
    cache_key = f"forecast:{lat:.4f}:{lon:.4f}:{units}"
    cached = await get_cached(cache_key)
    if cached:
        return ForecastResponse(**{**cached, "cached": True})

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            f"{settings.OPENWEATHER_BASE_URL}/forecast",
            params={
                "lat": lat,
                "lon": lon,
                "units": units,
                "appid": settings.OPENWEATHER_API_KEY,
            },
        )
        resp.raise_for_status()
        data = resp.json()

    forecast_items = [
        ForecastItem(
            dt=item["dt"],
            dt_txt=item["dt_txt"],
            weather=_parse_condition(item["weather"][0]),
            main=_parse_main(item["main"]),
            wind=_parse_wind(item.get("wind", {})),
            clouds=item["clouds"]["all"],
            pop=item.get("pop", 0.0),
        )
        for item in data["list"]
    ]

    result = ForecastResponse(
        city=data["city"]["name"],
        country=data["city"]["country"],
        lat=data["city"]["coord"]["lat"],
        lon=data["city"]["coord"]["lon"],
        units=units,
        forecast=forecast_items,
        cached=False,
    )

    await set_cached(cache_key, result.model_dump(), settings.CACHE_TTL_FORECAST)
    return result
