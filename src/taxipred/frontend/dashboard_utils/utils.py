import streamlit as st
import datetime
import requests
import base64, pathlib
import polyline
import os
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# ---------------- Bakgrundsbild ----------------
def set_bg(image_path: str):
    img_bytes = pathlib.Path(image_path).read_bytes()
    map_image = base64.b64encode(img_bytes).decode()
    st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{map_image}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        background-repeat: no-repeat;
        background-color: transparent !important;
    }}
    .block-container {{
        max-width: 1200px;
        margin: auto;
        padding-top: 3rem;
    }}
   
    </style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="Taxi Prediction", layout="wide")
set_bg("src/taxipred/frontend/assets/map_background.png")

# ---------------- Funktioner ----------------
def geocode_address(address: str):
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": GOOGLE_API_KEY}
    resp = requests.get(url, params=params).json()
    if resp.get("results"):
        loc = resp["results"][0]["geometry"]["location"]
        return loc["lat"], loc["lng"]
    return None, None


def get_time_of_day(time: datetime.time) -> str:
    hour = time.hour
    if 6 <= hour < 12:
        return "Morning"
    elif 12 <= hour < 18:
        return "Afternoon"
    elif 18 <= hour < 24:
        return "Evening"
    else:
        return "Night"
    

def fetch_address_suggestions(query: str):
    if not query:
        return []
    url = "https://maps.googleapis.com/maps/api/place/autocomplete/json"
    params = {
        "input": query,
        "types": "geocode",
        "components": "country:se",  # Begränsa till Sverige
        "key": GOOGLE_API_KEY
    }
    resp = requests.get(url, params=params).json()
    return [pred["description"] for pred in resp.get("predictions", [])]

def get_route_info(start_lat, start_lon, end_lat, end_lon):
    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": f"{start_lat},{start_lon}",
        "destination": f"{end_lat},{end_lon}",
        "mode": "driving",
        "key": GOOGLE_API_KEY
    }
    resp = requests.get(url, params=params).json()
    if resp.get("routes"):
        leg = resp["routes"][0]["legs"][0]
        distance_km = leg["distance"]["value"] / 1000
        duration_min = leg["duration"]["value"] / 60

        # Hämta polyline för rutten
        points = resp["routes"][0]["overview_polyline"]["points"]
        coords = polyline.decode(points)  # lista med (lat, lon)

        return distance_km, duration_min, coords
    return None, None, []