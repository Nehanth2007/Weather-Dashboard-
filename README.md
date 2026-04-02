# 🌤️ Weather Dashboard API

A production-ready REST API built with **FastAPI** that aggregates weather data from OpenWeatherMap, with **Redis caching** to minimize API quota usage.

## Features

- 🔍 **City search** — geocode any city name to lat/lon
- 🌡️ **Current weather** — temperature, humidity, wind, visibility, clouds
- 📅 **5-day forecast** — 3-hour interval forecasts with precipitation probability
- ⚡ **Redis caching** — smart TTLs per endpoint (10min current / 30min forecast / 24h geocoding)
- 🧱 **Pydantic v2 models** — full data validation and serialization
- 🌐 **Units support** — metric (°C), imperial (°F), or standard (K)
- 📖 **Auto docs** — Swagger UI at `/docs`, ReDoc at `/redoc`

## Tech Stack

| Layer        | Technology             |
|--------------|------------------------|
| Framework    | FastAPI                |
| HTTP client  | httpx (async)          |
| Cache        | Redis (redis-py async) |
| Validation   | Pydantic v2            |
| Config       | pydantic-settings      |
| Server       | Uvicorn                |

## Project Structure

```
weather-dashboard-api/
├── app/
│   ├── main.py               # FastAPI app + lifespan
│   ├── core/
│   │   ├── config.py         # Settings via .env
│   │   └── cache.py          # Redis client + helpers
│   ├── models/
│   │   └── weather.py        # Pydantic response models
│   ├── services/
│   │   └── weather_service.py # OWM API calls + cache logic
│   └── routers/
│       └── weather.py        # Route handlers
├── .env.example
├── requirements.txt
└── README.md
```

## Getting Started

### 1. Clone & install

```bash
git clone https://github.com/yourusername/weather-dashboard-api.git
cd weather-dashboard-api

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and add your [OpenWeatherMap API key](https://openweathermap.org/api) (free tier works).

### 3. Start Redis (Docker)

```bash
docker run -d -p 6379:6379 redis:alpine
```

> **Note:** Redis is optional. If unavailable, the API works without caching.

### 4. Run the server

```bash
uvicorn app.main:app --reload
```

Visit: [http://localhost:8000/docs](http://localhost:8000/docs)

## API Reference

### `GET /weather/search`
Search for cities by name.

| Param | Type   | Required | Description         |
|-------|--------|----------|---------------------|
| `q`   | string | ✅        | City name to search |

**Example:**
```
GET /weather/search?q=Mumbai
```

---

### `GET /weather/current`
Get current weather conditions.

| Param   | Type   | Required | Description              |
|---------|--------|----------|--------------------------|
| `city`  | string | ✅ or lat/lon | City name           |
| `lat`   | float  | ✅ or city   | Latitude            |
| `lon`   | float  | ✅ or city   | Longitude           |
| `units` | string | ❌        | metric / imperial / standard |

**Example:**
```
GET /weather/current?city=London&units=metric
GET /weather/current?lat=51.5074&lon=-0.1278
```

---

### `GET /weather/forecast`
Get 5-day / 3-hour interval forecast.

Same params as `/current`.

**Example:**
```
GET /weather/forecast?city=Delhi&units=metric
```

---

## Caching Strategy

| Endpoint     | Cache TTL  | Reason                        |
|-------------|------------|-------------------------------|
| `/current`  | 10 minutes | Weather changes frequently    |
| `/forecast` | 30 minutes | Forecast data is more stable  |
| `/search`   | 24 hours   | City coordinates don't change |

The `cached: true` field in responses tells you when data came from Redis.

## License

MIT
