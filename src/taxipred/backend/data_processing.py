from taxipred.utils.constants import TAXI_CSV_PATH
import pandas as pd
import json


class TaxiData:
    def __init__(self):
        self.df = pd.read_csv(TAXI_CSV_PATH)

    def to_json(self):
        return json.loads(self.df.to_json(orient = "records"))

#Cleaning the data. Dropping columns with important data and filling not so important columns with 'unknown'. 
def clean_taxi_data(df: pd.DataFrame) -> pd.DataFrame:
    df_cleaned = df.dropna(
        subset =[
        "Trip_Distance_km",
        "Base_Fare",
        "Per_Km_Rate",
        "Per_Minute_Rate",
        "Trip_Duration_Minutes",
        ]
    ).copy()

    for col in ["Time_of_Day", "Day_of_Week", "Traffic_Conditions", "Weather"]:
        df_cleaned[col] = df_cleaned[col].fillna("Unknown")

    #Swappping nan values in 'passenger_count' with the median value 
    if "Passenger_Count" in df_cleaned.columns:
        median_pass = df_cleaned["Passenger_Count"].median()
        df_cleaned["Passenger_Count"] = df_cleaned["Passenger_Count"].fillna(median_pass)

    return df_cleaned