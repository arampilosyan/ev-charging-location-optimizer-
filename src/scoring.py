"""Transparent first-pass candidate scoring; not a measured demand forecast."""
from math import radians, sin, cos, sqrt, atan2
import pandas as pd


def distance_km(lat1, lon1, lat2, lon2):
    """Great-circle distance between two points, in kilometres."""
    radius = 6371.0
    dlat = radians(float(lat2) - float(lat1))
    dlon = radians(float(lon2) - float(lon1))
    a = (
        sin(dlat / 2) ** 2
        + cos(radians(float(lat1))) * cos(radians(float(lat2)))
        * sin(dlon / 2) ** 2
    )
    return 2 * radius * atan2(sqrt(a), sqrt(max(0.0, 1 - a)))


def score_candidates(data):
    """Rank parking/mall candidates using distance to mapped chargers and place type."""
    if data.empty:
        return data.copy()

    stations = data[data["category"] == "Existing charger"]
    candidates = data[data["category"].isin(["Parking", "Shopping mall"])].copy()
    if candidates.empty:
        candidates["nearest_station_km"] = pd.Series(dtype=float)
        candidates["distance_score"] = pd.Series(dtype=float)
        candidates["type_bonus"] = pd.Series(dtype=float)
        candidates["score"] = pd.Series(dtype=float)
        return candidates

    distances = []
    for _, candidate in candidates.iterrows():
        if stations.empty:
            # Unknown competition is not proof of zero competition; mark a neutral capped distance.
            nearest = 5.0
        else:
            nearest = min(
                distance_km(candidate["latitude"], candidate["longitude"],
                            station["latitude"], station["longitude"])
                for _, station in stations.iterrows()
            )
        distances.append(nearest)

    candidates["nearest_station_km"] = distances
    candidates["distance_score"] = candidates["nearest_station_km"].clip(upper=5) / 5 * 70
    candidates["type_bonus"] = candidates["category"].map({
        "Shopping mall": 30,
        "Parking": 20,
    }).fillna(0)
    candidates["score"] = (candidates["distance_score"] + candidates["type_bonus"]).clip(upper=100)
    return candidates.sort_values("score", ascending=False).reset_index(drop=True)
