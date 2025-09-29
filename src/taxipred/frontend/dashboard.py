import streamlit as st
import datetime
import requests
from geopy.geocoders import Nominatim
import base64, pathlib

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
    geolocator = Nominatim(user_agent="taxi_app")
    location = geolocator.geocode(address)
    if location:
        return location.latitude, location.longitude
    return None, None

def get_route_info(start_lat, start_lon, end_lat, end_lon):
    url = f"http://router.project-osrm.org/route/v1/driving/{start_lon},{start_lat};{end_lon},{end_lat}?overview=false"
    resp = requests.get(url).json()
    if resp["code"] == "Ok":
        leg = resp["routes"][0]["legs"][0]
        distance_km = leg["distance"] / 1000
        duration_min = leg["duration"] / 60
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
st.title("🚖 Taxi Prediction")

col1, col2 = st.columns([1, 1])

with col1:
    start = st.text_input("Varifrån (adress)", "Drottninggatan 1, Stockholm")
    destination = st.text_input("Vart vill du åka?", "Centralstationen, Göteborg")
    date = st.date_input("Datum", datetime.date.today())
    time = st.time_input("Tid", value=datetime.time(8, 0))
    passengers = st.slider("Antal passagerare", 1, 4, 1)

    if st.button("Beräkna pris"):
        st.session_state["predict_request"] = {
            "start": start,
            "destination": destination,
            "date": date,
            "time": time,
            "passengers": passengers,
        }

with col2:
    if "predict_request" in st.session_state:
        req = st.session_state["predict_request"]

        # Geokoda adresser
        start_lat, start_lon = geocode_address(req["start"])
        end_lat, end_lon = geocode_address(req["destination"])

        if not start_lat or not end_lat:
            st.error("Kunde inte hitta en eller båda adresserna.")
        else:
            dist_km, dur_min = get_route_info(start_lat, start_lon, end_lat, end_lon)
            hours = int(dur_min // 60)
            minutes = int(dur_min % 60)
            total_duration = f"{hours} h  {minutes} min" if hours > 0 else f"{minutes} min"

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

                st.subheader(" Prediktion")
                
                response = requests.post("http://127.0.0.1:8000/taxi/predict", json=payload)

                if response.ok:
                    price = response.json().get("price", "okänt") * 10
                    st.success(f" Pris: {price:.2f} kr")
                    st.info(f" Avstånd: {dist_km:.1f} km") 
                    st.info(f"Tid: {total_duration}")
                else:
                    st.error("Något gick fel med prediktions-API:t.")
