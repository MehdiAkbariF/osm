# c:\Users\Raven\OSM\app\api\v2\schemas\map.py
from pydantic import BaseModel
from typing import List


class RouteRequest(BaseModel):
    start_lat: float
    start_lon: float
    end_lat: float
    end_lon: float


class LocationCoordinate(BaseModel):
    lat: float
    lon: float


class RouteOptimizeRequest(BaseModel):
    locations: List[LocationCoordinate]