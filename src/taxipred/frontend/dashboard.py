import streamlit as st
from taxipred.utils.helpers import read_api_endpoint
import pandas as pd
import datetime
import requests

data = read_api_endpoint("taxi")
df = pd.DataFrame(data.json())

def get_time(time: datetime.time) -> str:
    hour = time.hour
    if  6 <= hour < 12:
        return "Morning"
    elif 12 <= hour < 18:
        return "Afternoon"
    elif 18 <= hour < 24:
        return "Evening"
    else: 
        return "Night"

def main():
    
    st.markdown("<h2 style='text-align: center;'>Taxi Prediction</h2>", unsafe_allow_html=True)

    # 
    left, col1, col2, right = st.columns([1, 2, 2, 1])

    with col1:
        start = st.text_input("Varifrån (adress eller stad)")
        date = st.date_input("Datum", datetime.date.today())
        passengers = st.slider("Antal passagerare", 1, 4, 1)

    with col2:
        destination = st.text_input("Vart vill du åka?")
        time = st.time_input("Tid", value=datetime.time(0, 0))


        # Mockade Google API-värden
        st.write("📍 Avstånd: 5 km (mock)")
        st.write("⏱️ Restid: 12 min (mock)")

    # Knapp för att skicka till API
    if st.button("Beräkna pris"):
        time_of_day = get_time(time)
        day_of_week = date.strftime("%A")
        payload = {
            "Trip_Distance_km": 5,           # Mock-värde
            "Trip_Duration_Minutes": 12,     # Mock-värde
            "Time_of_Day": time_of_day,      
            "Day_of_Week": date.strftime("%A"),
            "Passenger_Count": passengers
        }
        st.json(payload)
        response = requests.post("http://127.0.0.1:8000/taxi/predict", json=payload)
    

if __name__ == "__main__":
    main()
