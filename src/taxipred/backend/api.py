from fastapi import FastAPI
from taxipred.backend.data_processing import TaxiData
from pydantic import BaseModel, Field
from taxipred.utils.constants import MODEL_PATH
import joblib
import pandas as pd
from taxipred.backend.data_processing import TaxiData

model = joblib.load(MODEL_PATH)
app = FastAPI()
taxi_data = TaxiData()

class TaxiInput(BaseModel):
    Trip_Distance_km: float = Field (gt=0)
    Time_of_Day: str
    Day_of_Week: str
    Passenger_Count: int = Field (gt=0, lt=5)
    Trip_Duration_Minutes: float

class PredictionOutput(BaseModel):
    Predicted_Trip_Price: float

@app.get("/taxi/")
def read_taxi_data():
    return taxi_data.to_json()
   
@app.post("/taxi/predict")
def predict_price(payload: TaxiInput):
    data_to_predict = pd.DataFrame(payload.model_dump(), index=[0])
    data_to_predict = pd.get_dummies(data_to_predict, drop_first=True)
    model = joblib.load(MODEL_PATH)
    data_to_predict = data_to_predict.reindex(columns=model.feature_names_in_, fill_value=0)
    prediciton = model.predict(data_to_predict)[0]

    return {"price": prediciton}                                         
    
    