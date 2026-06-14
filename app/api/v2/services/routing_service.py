# c:\Users\Raven\OSM\app\api\v2\services\routing_service.py
import httpx
from fastapi import HTTPException

OSRM_URL = "http://127.0.0.1:5000"

async def get_route(
    start_lat: float,
    start_lon: float,
    end_lat: float,
    end_lon: float
):
    url = f"{OSRM_URL}/route/v1/driving/{start_lon},{start_lat};{end_lon},{end_lat}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                url,
                params={
                    "overview": "full",
                    "geometries": "geojson",
                    "steps": "true" 
                },
                timeout=12.0
            )
            
            if response.status_code == 200:
                return response.json()
                
            raise HTTPException(
                status_code=response.status_code,
                detail="Error receiving route from OSRM engine"
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=502,
                detail=f"Unable to connect to OSRM server: {str(e)}"
            )


async def optimize_trip(locations: list[dict]):
    if len(locations) < 2:
        raise HTTPException(status_code=400, detail="At least 2 locations are required for routing")

    coords_string = ";".join([f"{loc['lon']},{loc['lat']}" for loc in locations])
    
    url = f"{OSRM_URL}/trip/v1/driving/{coords_string}"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                url,
                params={
                    "source": "first",
                    "destination": "any",
                    "overview": "full",
                    "geometries": "geojson",
                    "steps": "true"
                },
                timeout=15.0
            )
            
            if response.status_code == 200:
                return response.json()
                
            raise HTTPException(
                status_code=response.status_code,
                detail="Error optimizing trip from OSRM"
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=502,
                detail=f"Error connecting to OSRM trip service: {str(e)}"
            )