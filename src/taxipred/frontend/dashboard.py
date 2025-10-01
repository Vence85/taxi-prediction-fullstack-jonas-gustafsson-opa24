import streamlit as st
import datetime
import requests
import base64, pathlib
from dotenv import load_dotenv
import os
load_dotenv()
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

# Routing
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
        return distance_km, duration_min
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

# ---------------- Layout ----------------
st.title("Taxi price app")

col1, col2 = st.columns([1, 1])

with col1:
    start = st.text_input("Varifrån (adress)")
    destination = st.text_input("Vart vill du åka?")
    date = st.date_input("Datum", datetime.date.today())
    time = st.time_input("Tid", value=datetime.time(8, 0))
    passengers = st.slider("Antal passagerare", 1, 4, 1)

    if st.button("Beräkna pris"):
        # Spara inputs temporärt till session_state så col2 kan läsa dem
        st.session_state["inputs"] = {
            "start": start,
            "destination": destination,
            "date": date,
            "time": time,
            "passengers": passengers,
        }


with col2:
    if "inputs" in st.session_state:
        req = st.session_state["inputs"]

        # Geokoda adresser
        start_lat, start_lon = geocode_address(req["start"])
        end_lat, end_lon = geocode_address(req["destination"])

        if not start_lat or not end_lat:
            st.error("Kunde inte hitta en eller båda adresserna.")
        else:
            dist_km, dur_min = get_route_info(start_lat, start_lon, end_lat, end_lon)
            hours = int(dur_min // 60)
            minutes = int(dur_min % 60)
            total_duration = f"{hours} h {minutes} min" if hours > 0 else f"{minutes} min"

            if dist_km and dur_min:
                time_of_day = get_time_of_day(req["time"])
                day_of_week = req["date"].strftime("%A")

                payload = {
                    "Trip_Distance_km": round(dist_km, 2),
                    "Trip_Duration_Minutes": round(dur_min, 1),
                    "Day_of_Week": day_of_week,
                    "Time_of_Day": time_of_day,
                    "Passenger_Count": req["passengers"],
                }

                st.subheader("Prediction")
                response = requests.post("http://127.0.0.1:8000/taxi/predict", json=payload)

                if response.ok:
                    price = response.json().get("price", "okänt") * 10
                    st.success(f"Pris: {price:.2f} sek")
                    st.info(f"Avstånd: {dist_km:.1f} km")
                    st.info(f"Tid: {total_duration}")
                else:
                    st.error("Något gick fel med prediktions-API:t.")