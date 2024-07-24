from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime, timedelta
import pandas as pd
import pickle
from tensorflow.keras.models import load_model
from pytorch_tabnet.tab_model import TabNetRegressor
import uvicorn

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
