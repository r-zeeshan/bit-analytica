from tensorflow.keras.models import load_model
from pytorch_tabnet.tab_model import TabNetRegressor
from datetime import datetime, timedelta
import pandas as pd
import pickle
import os
from plot_utils import plot_all_indicators, plot_with_sma, plot_with_ema, plot_with_rsi, plot_with_macd, plot_with_bollinger_bands, plot_with_atr, plot_with_stochastic, plot_with_obv


def load_models():
    """
    Load the pre-trained models and scalers used for prediction.

    Returns:
        x_scaler (object): The scaler used for scaling the input features.
        y_high_scaler (object): The scaler used for scaling the high prediction target.
        y_low_scaler (object): The scaler used for scaling the low prediction target.
        high_model (object): The pre-trained model for high prediction.
        low_model (object): The pre-trained model for low prediction.
    """

    with open('models/scalers/x_scaler.pkl', 'rb') as f:
        x_scaler = pickle.load(f)

    with open('models/scalers/y_high_scaler.pkl', 'rb') as f:
        y_high_scaler = pickle.load(f)

    with open('models/scalers/y_low_scaler.pkl', 'rb') as f:
        y_low_scaler = pickle.load(f)

    high_model = load_model('models/high/high.keras')
    low_model = TabNetRegressor()
    low_model.load_model('models/low/low.zip')

    return x_scaler, y_high_scaler, y_low_scaler, high_model, low_model


def getData(textDataPipeline, bitcoinDataPipeline, scaler):
    """
    Retrieves the latest Bitcoin data and sentiment score, combines them into a DataFrame,
    and applies scaling to the data.

    Parameters:
    - textDataPipeline: An object representing the text data pipeline.
    - bitcoinDataPipeline: An object representing the Bitcoin data pipeline.
    - scaler: An object used for scaling the data.

    Returns:
    - Transformed data: A DataFrame containing the transformed data.

    """
    sentiment_score = textDataPipeline.getSentimentScoreForPast24Hours()
    bitcoin_data = bitcoinDataPipeline.getLatestBitcoinData()
    
    date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    try:
        bitcoin_data = bitcoin_data.loc[date]
        sentiment_score = sentiment_score.loc[date]
    except KeyError:
        try:
            bitcoin_data = bitcoin_data.iloc[-2]
            sentiment_score = sentiment_score.iloc[-2]
        except IndexError:
            bitcoin_data = bitcoin_data.iloc[-1]
            sentiment_score = sentiment_score.iloc[-1]

    data = pd.DataFrame([pd.concat([bitcoin_data, sentiment_score], axis=0)])
    return scaler.transform(data)



def predict_price(model, data, scaler, flag=False):
    """
    Predicts the price using the given model, data, and scaler.

    Parameters:
    - model: The trained model used for prediction.
    - data: The input data for prediction.
    - scaler: The scaler used to scale the data.
    - flag: A boolean flag indicating whether the data needs to be reshaped.

    Returns:
    - The predicted price as a single value.
    """
    if flag:
        data = data.reshape((data.shape[0], 1, data.shape[1]))
    pred = model.predict(data)
    pred = scaler.inverse_transform(pred)
    return pred.flatten()[0]

def plot_hourly_data(bitcoinDataPipeline):
    """
    Plots the hourly data for Bitcoin.

    Args:
        bitcoinDataPipeline: An instance of the BitcoinDataPipeline class.

    Returns:
        fig: The matplotlib figure object containing the plotted data.
    """
    hourly_data = bitcoinDataPipeline.getHourlyData()
    start_date = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')
    fig = plot_all_indicators(hourly_data, start_date, end_date, prediction_file='data/predictions.csv')
    return fig



def plot_daily_data(bitcoinDataPipeline, start_date, end_date):
    """
    Plots various technical indicators based on daily Bitcoin data.

    Args:
        bitcoinDataPipeline (object): An object representing the Bitcoin data pipeline.
        start_date (str): The start date for the data range.
        end_date (str): The end date for the data range.

    Returns:
        list: A list of plots for each technical indicator.

    """
    from config import SMA7, SMA14, EMA7, EMA14, RSI, MACD, SIGNAL_LINE ,BOLLINGER_SMA
    from config import UPPER_BAND_BB, LOWER_BAND_BB, ATR, K, D, OBV
    daily_data = bitcoinDataPipeline.getLatestBitcoinData()
    plots = []
    plots.append(plot_with_sma(daily_data, start_date, end_date, SMA7, SMA14))
    plots.append(plot_with_ema(daily_data, start_date, end_date, EMA7, EMA14))
    plots.append(plot_with_rsi(daily_data, start_date, end_date, RSI))
    plots.append(plot_with_macd(daily_data, start_date, end_date, MACD, SIGNAL_LINE))
    plots.append(plot_with_bollinger_bands(daily_data, start_date, end_date, BOLLINGER_SMA, UPPER_BAND_BB, LOWER_BAND_BB))
    plots.append(plot_with_atr(daily_data, start_date, end_date, ATR))
    plots.append(plot_with_stochastic(daily_data, start_date, end_date, K, D))
    plots.append(plot_with_obv(daily_data, start_date, end_date, OBV))
    return plots


def save_predictions(high_pred, low_pred):
    """
    Saves the predictions to a CSV file in the data folder.

    Args:
        high_pred (float): Predicted high price.
        low_pred (float): Predicted low price.
    """
    os.makedirs('data', exist_ok=True)
    file_path = os.path.join('data', 'predictions.csv')
    current_date = datetime.now().strftime('%Y-%m-%d')
    
    new_data = pd.DataFrame({
        'date': [current_date],
        'predicted_high': [high_pred],
        'predicted_low': [low_pred]
    })

    if os.path.exists(file_path):
        existing_data = pd.read_csv(file_path)

        if current_date in existing_data['date'].values:
            existing_data.loc[existing_data['date'] == current_date, ['predicted_high', 'predicted_low']] = [high_pred, low_pred]
        else:
            existing_data = pd.concat([existing_data, new_data], ignore_index=True)
        
        existing_data.to_csv(file_path, index=False)
    else:
        new_data.to_csv(file_path, index=False)