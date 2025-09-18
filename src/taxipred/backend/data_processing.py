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
    cleaned_df = df.dropna(
        subset =[
        "Trip_Distance_km",
        "Base_Fare",
        "Per_Km_Rate",
        "Per_Minute_Rate",
        "Trip_Duration_Minutes",
        ]
    ).copy()

    for col in ["Time_of_Day", "Day_of_Week", "Traffic_Conditions", "Weather"]:
        cleaned_df[col] = cleaned_df[col].fillna("Unknown")

    #Swappping nan values in 'passenger_count' with the median value 
    if "Passenger_Count" in cleaned_df.columns:
        median_pass = cleaned_df["Passenger_Count"].median()
        cleaned_df["Passenger_Count"] = cleaned_df["Passenger_Count"].fillna(median_pass)

    #cleaned_df is now a dataframe where all nan, except in the target column, are dropped or unknow. Passanger_count nans is set to median
    #Creates a dataframe with the rows where target is nan. 
    predict_df = cleaned_df[cleaned_df["Trip_Price"].isna()]

    # Completely cleaned dataframe with no nans
    train_df = cleaned_df.dropna(subset=["Trip_Price"])

    Q1 = train_df["Trip_Price"].quantile(0.25)
    Q3 = train_df["Trip_Price"].quantile(0.75)
    IQR = Q3 - Q1

    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    train_df = train_df[(train_df["Trip_Price"] >= lower_bound) & (train_df["Trip_Price"] <= upper_bound)]
    
    return cleaned_df, train_df, predict_df