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
    from tensorflow.keras.models import load_model
    from pytorch_tabnet.tab_model import TabNetRegressor
    import pickle

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
    
    from datetime import datetime, timedelta
    date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    bitcoin_data = bitcoin_data.loc[date]
    sentiment_score = sentiment_score.loc[date]

    import pandas as pd
    data =  pd.DataFrame([pd.concat([bitcoin_data, sentiment_score], axis= 0)])
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
