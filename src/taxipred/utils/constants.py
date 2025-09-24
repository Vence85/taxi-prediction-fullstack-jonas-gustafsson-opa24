from importlib.resources import files
from pathlib import Path
TAXI_CSV_PATH = files("taxipred").joinpath("data/taxi_trip_pricing.csv")
MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "taxi_price_predictor.joblib"

# DATA_PATH = Path(__file__).parents[1] / "data"
print(MODEL_PATH)