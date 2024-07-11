def load_models():
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
    sentiment_score = textDataPipeline.getSentimentScoreForPast24Hours()
    bitcoin_data = bitcoinDataPipeline.getLatestBitcoinData()

    bitcoin_data = bitcoin_data.iloc[-2]
    sentiment_score = sentiment_score.iloc[-2]

    import pandas as pd
    data =  pd.DataFrame([pd.concat([bitcoin_data, sentiment_score], axis= 0)])
    return scaler.transform(data)


def predict_price(model, data, scaler, flag=False):
    if flag:
        data = data.reshape((data.shape[0], 1, data.shape[1]))
    pred = model.predict(data)
    pred = scaler.inverse_transform(pred)
    return pred.flatten()[0]


# data = getData(textDataPipeline, bitcoinDataPipeline, x_scaler)

# print(f"High: {predict_price(high_model, data, y_high_scaler, flag=True)}")
# print(f"Low: {predict_price(low_model, data, y_high_scaler, flag=False)}")
