from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime, timedelta
import pandas as pd
import pickle
from tensorflow.keras.models import load_model
from pytorch_tabnet.tab_model import TabNetRegressor

app = FastAPI()

# Load models and scalers
x_scaler, y_high_scaler, y_low_scaler, high_model, low_model = None, None, None, None, None

def load_models():
    global x_scaler, y_high_scaler, y_low_scaler, high_model, low_model

    with open('models/scalers/x_scaler.pkl', 'rb') as f:
        x_scaler = pickle.load(f)

    with open('models/scalers/y_high_scaler.pkl', 'rb') as f:
        y_high_scaler = pickle.load(f)

    with open('models/scalers/y_low_scaler.pkl', 'rb') as f:
        y_low_scaler = pickle.load(f)

    high_model = load_model('models/high/high.keras')
    low_model = TabNetRegressor()
    low_model.load_model('models/low/low.zip')

load_models()

class InputData(BaseModel):
    sentiment_score: float
    open: float
    high: float
    low: float
    close: float
    adj_close: float
    volume: float
    sma_7: float
    sma_14: float
    ema_7: float
    ema_14: float
    rsi: float
    macd: float
    signal_line: float
    bollinger_sma: float
    upper_band_bb: float
    lower_band_bb: float
    atr: float
    k: float
    d: float
    obv: float

@app.post("/predict/")
def predict(data: InputData):
    input_df = pd.DataFrame([data.dict()])
    scaled_input = x_scaler.transform(input_df)

    high_pred = high_model.predict(scaled_input.reshape((scaled_input.shape[0], 1, scaled_input.shape[1])))
    low_pred = low_model.predict(scaled_input)

    high_pred = y_high_scaler.inverse_transform(high_pred)
    low_pred = y_low_scaler.inverse_transform(low_pred)

    return {
        "predicted_high": high_pred.flatten()[0],
        "predicted_low": low_pred.flatten()[0]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
