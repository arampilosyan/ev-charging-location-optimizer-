# EV Charging Location Optimizer — Yerevan

Python/Streamlit project for exploring possible EV charging locations in Yerevan, Armenia.

## Features

- Fetches charging stations, parking places, shopping malls and fuel stations mapped in OpenStreetMap.
- Displays mapped chargers and candidate locations on an interactive map.
- Ranks candidate locations with a transparent first-pass heuristic.
- Compares configurable AC/DC financial scenarios and budget fit.
- Includes automated tests for financial calculations.

## Tech stack

Python, Streamlit, Pandas, Requests, Folium, Streamlit-Folium, Pytest, OpenStreetMap Overpass API.

## Run locally (macOS/Linux)

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

Run tests:

```bash
pytest -v
```

## Data and limitations

- Map objects are fetched live from OpenStreetMap using Overpass API.
- The geographic bounding box is approximate, not an official Yerevan boundary.
- OSM can be incomplete or outdated. A mapped charging station is not guaranteed to be operational.
- The candidate score is a heuristic based on distance to mapped chargers and type of place. It is not a validated demand forecast.
- Default hardware and financial values are illustrative placeholders, not verified current quotations or tariffs. Replace them with written supplier, utility, landlord and operator quotes before any investment decision.
- The simple model does not yet include taxes, payment fees, grid upgrade costs, financing, downtime, VAT, depreciation, or seasonal utilization.
- OpenStreetMap data attribution: © OpenStreetMap contributors, https://www.openstreetmap.org/copyright. Follow the OSM attribution and ODbL requirements when using its data.

## Next development steps

1. Add real supplier quotations and local electricity tariff inputs.
2. Add road access, demand proxies, charger power and competitor checks.
3. Add a location-selection optimization model under the AMD 5–10 million budget.
4. Validate assumptions against on-site checks and actual utilization data.
