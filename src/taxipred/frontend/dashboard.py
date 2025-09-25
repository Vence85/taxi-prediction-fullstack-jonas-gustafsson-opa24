import streamlit as st
from taxipred.utils.helpers import read_api_endpoint
import pandas as pd
import requests
import streamlit as st
import datetime

data = read_api_endpoint("taxi")
df = pd.DataFrame(data.json())

def main():
    

    # Välj datum
    date = st.date_input(
        "Välj datum för resan",
        datetime.date.today()
    )

    # Välj tid
    time = st.time_input(
        "Välj tid för resan",
        datetime.datetime.now().time()
    )



if __name__ == "__main__":
    main()
