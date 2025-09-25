import streamlit as st
from taxipred.utils.helpers import read_api_endpoint
import pandas as pd
import requests

data = read_api_endpoint("taxi")
df = pd.DataFrame(data.json())

def main():
    st.markdown("# Taxi Prediction Dashboard")
    # Testa /taxi/
    st.dataframe(df)

    # Testa /taxi/predict
    st.markdown("---")
    st.subheader("Snabb prediktionstest")
  


if __name__ == "__main__":
    main()
