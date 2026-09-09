"""
External API Adapters & Live Data Providers.
Supports:
- Gemini LLM (models/gemini-2.5-flash) for executive risk explanations
- AviationStack for real-time flight telemetry
- NewsData.io for global supply chain incident intelligence
- OpenWeatherMap for live atmospheric conditions

Architecture:
External API -> Provider Adapter -> Normalized Signal -> Risk Engine
If external API fails or is unconfigured: Transparently falls back to synthetic provider.
"""
from __future__ import annotations

import os
from typing import Any
from pathlib import Path
import httpx
from dotenv import load_dotenv

load_dotenv()
load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

from app.config import settings


# ─────────────────────────────────────────────────────────────
# 1. GEMINI LLM PROVIDER
# ─────────────────────────────────────────────────────────────
class GeminiLLMProvider:
    """Uses Google Gemini API for operational risk explanations and reroute rationale."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("LLM_API_KEY", "")
        self.endpoint = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

    def is_available(self) -> bool:
        return bool(self.api_key and len(self.api_key) > 10)

    def generate_explanation(self, prompt: str, max_tokens: int = 256) -> str | None:
        """Call Gemini to generate operational narrative."""
        if not self.is_available():
            return None

        url = f"{self.endpoint}?key={self.api_key}"
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": f"You are an expert AI logistics and supply chain optimization assistant. Keep your response concise, tactical, and operational (1-3 sentences).\n\n{prompt}"
                        }
                    ]
                }
            ],
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": 0.2,
            },
        }

        try:
            with httpx.Client(timeout=4.0) as client:
                res = client.post(url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        content = candidates[0].get("content", {})
                        parts = content.get("parts", [])
                        if parts:
                            return parts[0].get("text", "").strip()
        except Exception as e:
            # Non-blocking graceful fallback
            pass
        return None


# ─────────────────────────────────────────────────────────────
# 2. FLIGHT TELEMETRY (AviationStack)
# ─────────────────────────────────────────────────────────────
class AviationStackFlightProvider:
    """Queries AviationStack for live flight status and delay tracking."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("FLIGHT_API_KEY", "")
        self.base_url = "http://api.aviationstack.com/v1/flights"

    def is_available(self) -> bool:
        return bool(self.api_key and len(self.api_key) > 10)

    def get_live_flights(self, limit: int = 10) -> list[dict[str, Any]]:
        """Fetch active commercial freight/cargo flights."""
        if not self.is_available():
            return []

        params = {
            "access_key": self.api_key,
            "limit": limit,
        }

        try:
            with httpx.Client(timeout=3.0) as client:
                res = client.get(self.base_url, params=params)
                if res.status_code == 200:
                    data = res.json().get("data", [])
                    flights = []
                    for f in data:
                        dep = f.get("departure", {}) or {}
                        arr = f.get("arrival", {}) or {}
                        flight_info = f.get("flight", {}) or {}
                        delay_dep = dep.get("delay") or 0
                        status = f.get("flight_status", "active").upper()

                        flights.append({
                            "flight_number": flight_info.get("iata") or flight_info.get("icao") or "CARGO",
                            "origin_airport": dep.get("iata") or dep.get("airport") or "ORIGIN",
                            "destination_airport": arr.get("iata") or arr.get("airport") or "DEST",
                            "status": status,
                            "delay_minutes": int(delay_dep) if delay_dep else 0,
                            "scheduled_departure": dep.get("scheduled"),
                            "live": True,
                        })
                    return flights
        except Exception:
            pass
        return []


# ─────────────────────────────────────────────────────────────
# 3. GLOBAL INCIDENTS & NEWS (NewsData.io)
# ─────────────────────────────────────────────────────────────
class NewsDataProvider:
    """Queries NewsData.io for real-time supply chain and logistics disruptions."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("NEWS_API_KEY", "")
        self.endpoint = "https://newsdata.io/api/1/news"

    def is_available(self) -> bool:
        return bool(self.api_key and len(self.api_key) > 10)

    def get_logistics_alerts(self, query: str = "logistics OR shipping OR port strike", limit: int = 5) -> list[dict[str, Any]]:
        """Fetch active disruption headlines."""
        if not self.is_available():
            return []

        params = {
            "apikey": self.api_key,
            "q": query,
            "language": "en",
        }

        try:
            with httpx.Client(timeout=3.0) as client:
                res = client.get(self.endpoint, params=params)
                if res.status_code == 200:
                    data = res.json()
                    results = data.get("results", [])
                    alerts = []
                    for art in results[:limit]:
                        alerts.append({
                            "title": art.get("title", ""),
                            "source": art.get("source_id", "News"),
                            "pub_date": art.get("pubDate", ""),
                            "link": art.get("link", ""),
                            "description": art.get("description", "")[:200] if art.get("description") else "",
                            "category": "external_intel",
                        })
                    return alerts
        except Exception:
            pass
        return []


# ─────────────────────────────────────────────────────────────
# 4. WEATHER PROVIDER (OpenWeatherMap)
# ─────────────────────────────────────────────────────────────
class OpenWeatherProvider:
    """Queries OpenWeatherMap for live atmospheric conditions."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("WEATHER_API_KEY", "")
        self.endpoint = "https://api.openweathermap.org/data/2.5/weather"

    def is_available(self) -> bool:
        return bool(self.api_key and len(self.api_key) > 10)

    def get_city_weather(self, city: str) -> dict[str, Any] | None:
        """Fetch live weather metrics for a city."""
        if not self.is_available():
            return None

        params = {
            "q": city,
            "appid": self.api_key,
            "units": "metric",
        }

        try:
            with httpx.Client(timeout=3.0) as client:
                res = client.get(self.endpoint, params=params)
                if res.status_code == 200:
                    data = res.json()
                    main = data.get("main", {})
                    weather_desc = (data.get("weather", [{}])[0]).get("main", "Clear")
                    wind = data.get("wind", {})

                    return {
                        "city": city,
                        "condition": weather_desc,
                        "temperature_c": main.get("temp"),
                        "humidity": main.get("humidity"),
                        "wind_speed_ms": wind.get("speed"),
                        "live": True,
                    }
        except Exception:
            pass
        return None
