import os
from typing import Dict
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_KEY: str = ""
    FRONTEND_URL: str = "http://localhost:5173"
    DATA_MODE: str = "auto"
    RANDOM_SEED: int = 42
    WEATHER_API_KEY: str = ""
    FLIGHT_API_KEY: str = ""
    NEWS_API_KEY: str = ""
    LLM_API_KEY: str = ""
    ROUTING_API_KEY: str = ""
    RISK_WEIGHT_WEATHER: float = 0.20
    RISK_WEIGHT_TRAFFIC: float = 0.15
    RISK_WEIGHT_CONGESTION: float = 0.20
    RISK_WEIGHT_TRANSPORT: float = 0.15
    RISK_WEIGHT_EXTERNAL: float = 0.10
    RISK_WEIGHT_HISTORICAL: float = 0.10
    RISK_WEIGHT_SHIPMENT: float = 0.10
    RISK_LOW_MAX: float = 3.0
    RISK_MEDIUM_MAX: float = 5.0
    RISK_HIGH_MAX: float = 7.5
    ROUTE_BALANCED_TIME: float = 0.45
    ROUTE_BALANCED_DISTANCE: float = 0.20
    ROUTE_BALANCED_RISK: float = 0.35
    ROUTE_FASTEST_TIME: float = 0.75
    ROUTE_FASTEST_DISTANCE: float = 0.10
    ROUTE_FASTEST_RISK: float = 0.15
    ROUTE_SAFEST_TIME: float = 0.15
    ROUTE_SAFEST_DISTANCE: float = 0.10
    ROUTE_SAFEST_RISK: float = 0.75

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

RISK_WEIGHTS: Dict[str, float] = {
    "weather": settings.RISK_WEIGHT_WEATHER,
    "traffic": settings.RISK_WEIGHT_TRAFFIC,
    "congestion": settings.RISK_WEIGHT_CONGESTION,
    "transport": settings.RISK_WEIGHT_TRANSPORT,
    "external": settings.RISK_WEIGHT_EXTERNAL,
    "historical": settings.RISK_WEIGHT_HISTORICAL,
    "shipment": settings.RISK_WEIGHT_SHIPMENT,
}

