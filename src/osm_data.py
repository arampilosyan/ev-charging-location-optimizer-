"""Download mapped charging stations and candidate places from OpenStreetMap."""
import requests
import pandas as pd

# Approximate Yerevan bounding box; not an official administrative boundary.
SOUTH, WEST = 40.07, 44.37
NORTH, EAST = 40.24, 44.62
OVERPASS_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]

COLUMNS = [
    "osm_id", "name", "category", "latitude", "longitude",
    "operator", "power", "source",
]


def fetch_yerevan_data():
    """Return OSM objects in the approximate Yerevan bounding box."""
    query = f"""
    [out:json][timeout:60];
    (
      nwr["amenity"="charging_station"]({SOUTH},{WEST},{NORTH},{EAST});
      nwr["amenity"="parking"]({SOUTH},{WEST},{NORTH},{EAST});
      nwr["shop"="mall"]({SOUTH},{WEST},{NORTH},{EAST});
      nwr["amenity"="fuel"]({SOUTH},{WEST},{NORTH},{EAST});
    );
    out center tags;
    """
    last_error = None
    for url in OVERPASS_URLS:
        try:
            response = requests.post(
                url,
                data={"data": query},
                headers={"User-Agent": "EVChargingLocationOptimizer/1.0 (educational project)"},
                timeout=90,
            )
            response.raise_for_status()
            elements = response.json().get("elements", [])
            records = []
            for element in elements:
                tags = element.get("tags", {})
                if "lat" in element and "lon" in element:
                    lat, lon = element["lat"], element["lon"]
                elif "center" in element:
                    lat, lon = element["center"]["lat"], element["center"]["lon"]
                else:
                    continue

                if tags.get("amenity") == "charging_station":
                    category = "Existing charger"
                elif tags.get("shop") == "mall":
                    category = "Shopping mall"
                elif tags.get("amenity") == "fuel":
                    category = "Fuel station"
                else:
                    category = "Parking"

                records.append({
                    "osm_id": element.get("id"),
                    "name": tags.get("name", "Unnamed place"),
                    "category": category,
                    "latitude": float(lat),
                    "longitude": float(lon),
                    "operator": tags.get("operator", "Unknown"),
                    "power": tags.get("charging_station:output", "Unknown"),
                    "source": "OpenStreetMap",
                })
            return pd.DataFrame(records, columns=COLUMNS)
        except (requests.RequestException, ValueError) as exc:
            last_error = exc
    raise RuntimeError(f"Could not fetch OSM data from available Overpass endpoints: {last_error}")
