import streamlit as st
import datetime
import requests
from dotenv import load_dotenv
from streamlit_searchbox import st_searchbox
import folium
from streamlit_folium import st_folium
from taxipred.frontend.dashboard_utils.utils import set_bg, geocode_address, get_time_of_day, fetch_address_suggestions, get_route_info
load_dotenv()

st.set_page_config(page_title="Taxi Prediction", layout="wide")
set_bg("src/taxipred/frontend/assets/map_background.png")

# ---------------- Layout ----------------
st.title("Taxi prediciton")

col1, col2 = st.columns([1, 1])
with col1:
    start = st_searchbox(
        search_function=fetch_address_suggestions,
        placeholder="Varifrån (adress)",
        key="start_search"
    )

    destination = st_searchbox(
        search_function=fetch_address_suggestions,
        placeholder="Vart vill du åka?",
        key="dest_search"
    )

    date = st.date_input("Datum", datetime.date.today())
    time = st.time_input("Tid", value=datetime.time(8, 0))
    passengers = st.slider("Antal passagerare", 1, 4, 1)

    if st.button("Beräkna pris"):
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
            dist_km, dur_min, coords = get_route_info(start_lat, start_lon, end_lat, end_lon)
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

                    # --- Karta med rutten ---
                    if coords:
                        midpoint = [(start_lat + end_lat) / 2, (start_lon + end_lon) / 2]
                        m = folium.Map(location=midpoint, zoom_start=10)
                        folium.PolyLine(coords, color="blue", weight=5).add_to(m)
                        folium.Marker([start_lat, start_lon], tooltip="Start").add_to(m)
                        folium.Marker([end_lat, end_lon], tooltip="Destination").add_to(m)
                        st_folium(m, width=700, height=500)
                else:
                    st.error("Något gick fel med prediktions-API:t.")