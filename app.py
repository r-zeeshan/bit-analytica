

import streamlit as st
import requests
from datetime import datetime, timedelta
import pytz
from text_data_pipeline import TextDataPipeline
from btc_data_pipeline import BitcoinDataPipeline
from config import LLM
from plot_utils import plot_all_indicators, plot_with_sma, plot_with_ema, plot_with_rsi, plot_with_macd, plot_with_bollinger_bands, plot_with_atr, plot_with_stochastic, plot_with_obv

@st.cache_resource
def initialize_pipelines():
    """
    Initializes the pipelines required for text and Bitcoin data processing.

    Returns:
        textDataPipeline (TextDataPipeline): The pipeline for text data processing.
        bitcoinDataPipeline (BitcoinDataPipeline): The pipeline for Bitcoin data processing.
    """
    textDataPipeline = TextDataPipeline(LLM)
    bitcoinDataPipeline = BitcoinDataPipeline()

    return textDataPipeline, bitcoinDataPipeline

def getData(textDataPipeline, bitcoinDataPipeline):
    """
    Retrieves the latest Bitcoin data and sentiment score, combines them into a DataFrame.

    Parameters:
    - textDataPipeline: An object representing the text data pipeline.
    - bitcoinDataPipeline: An object representing the Bitcoin data pipeline.

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
    return data

def get_predictions(data):
    """
    Sends data to the FastAPI backend and retrieves the predictions.

    Parameters:
    - data: The input data for prediction.

    Returns:
    - The predicted high and low prices.
    """
    response = requests.post("http://localhost:8000/predict/", json=data.to_dict(orient="records")[0])
    predictions = response.json()
    return predictions["predicted_high"], predictions["predicted_low"]

def plot_hourly_data(bitcoinDataPipeline):
    hourly_data = bitcoinDataPipeline.getHourlyData()
    start_date = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')
    fig = plot_all_indicators(hourly_data, start_date, end_date)
    return fig

def plot_daily_data(bitcoinDataPipeline, start_date, end_date):
    daily_data = bitcoinDataPipeline.getLatestBitcoinData()
    plots = []
    plots.append(plot_with_sma(daily_data, start_date, end_date))
    plots.append(plot_with_ema(daily_data, start_date, end_date))
    plots.append(plot_with_rsi(daily_data, start_date, end_date))
    plots.append(plot_with_macd(daily_data, start_date, end_date))
    plots.append(plot_with_bollinger_bands(daily_data, start_date, end_date))
    plots.append(plot_with_atr(daily_data, start_date, end_date))
    plots.append(plot_with_stochastic(daily_data, start_date, end_date))
    plots.append(plot_with_obv(daily_data, start_date, end_date))
    return plots

timezone = pytz.timezone("America/New_York")
st.set_page_config(layout="wide", page_title="BitAnalytica")
st.markdown(
    """
    <div style="text-align: center; padding-top: 30px;">
        <h1>BitAnalytica</h1>
    </div>
    """,
    unsafe_allow_html=True
)

textDataPipeline, bitcoinDataPipeline = initialize_pipelines()
if 'high_pred' not in st.session_state or 'low_pred' not in st.session_state:
    st.session_state.high_pred = None
    st.session_state.low_pred = None

col1, col2 = st.columns([8, 2])

with col1:
    st.markdown(
        """
        <div style="text-align: center; justify-content: center; padding-left: 300px">
            <h3>Bitcoin Hourly Data with Technical Indicators</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    fig = plot_hourly_data(bitcoinDataPipeline)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown(
        """
        <div style="padding-top: 80px;">
            <h3>Predictions</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    prediction_placeholder = st.empty()

    if st.session_state.high_pred is None or st.session_state.low_pred is None:
        prediction_placeholder.markdown(f"""
            <div style="display: flex; align-items: center; justify-content: center; height: 100%; flex-direction: column; padding-top: 80px;">
                <div style="background-color: #f0f0f0; color: black; padding: 10px 20px; margin: 10px; border-radius: 5px; text-align: center;">
                    Predicting...
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        data = getData(textDataPipeline, bitcoinDataPipeline)
        high_pred, low_pred = get_predictions(data)
        
        st.session_state.high_pred = high_pred
        st.session_state.low_pred = low_pred
        
        prediction_placeholder.markdown(f"""
            <div style="display: flex; align-items: center; justify-content: center; height: 100%; flex-direction: column; padding-top: 140px;">
                <div style="background-color: #13a9bd; color: white; padding: 10px 20px; margin: 10px; border-radius: 5px; text-align: center;">
                    Predicted High: ${st.session_state.high_pred:.2f}
                </div>
                                <div style="background-color: #c92516; color: white; padding: 10px 20px; margin: 10px; border-radius: 5px; text-align: center;">
                    Predicted Low: ${st.session_state.low_pred:.2f}
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        prediction_placeholder.markdown(f"""
            <div style="display: flex; align-items: center; justify-content: center; height: 100%; flex-direction: column; padding-top: 140px;">
                <div style="background-color: #13a9bd; color: white; padding: 10px 20px; margin: 10px; border-radius: 5px; text-align: center;">
                    Predicted High: ${st.session_state.high_pred:.2f}
                </div>
                <div style="background-color: #c92516; color: white; padding: 10px 20px; margin: 10px; border-radius: 5px; text-align: center;">
                    Predicted Low: ${st.session_state.low_pred:.2f}
                </div>
            </div>
        """, unsafe_allow_html=True)

current_time = datetime.now(timezone)
start_date = (datetime.now() - timedelta(days=45)).strftime('%Y-%m-%d')
end_date = datetime.now().strftime('%Y-%m-%d')
daily_plots = plot_daily_data(bitcoinDataPipeline, start_date, end_date)

st.markdown(
    """
    <div style="text-align: center;">
        <h2>Bitcoin Technical Analysis Daily Chart (Last 45 Days)</h2>
    </div>
    """,
    unsafe_allow_html=True
)
for i in range(0, len(daily_plots), 2):
    cols = st.columns(2)
    for col, plot in zip(cols, daily_plots[i:i+2]):
        col.plotly_chart(plot, use_container_width=True)

# Check if it's time to update the predictions and plots (every 24 hours at 7 AM UTC-4)
if current_time.hour == 7 and current_time.minute == 0:
    data = getData(textDataPipeline, bitcoinDataPipeline)
    high_pred, low_pred = get_predictions(data)
    st.session_state.high_pred = high_pred
    st.session_state.low_pred = low_pred

    prediction_placeholder.markdown(f"""
        <div style="display: flex; align-items: center; justify-content: center; height: 100%; flex-direction: column; padding-top: 140px;">
            <div style="background-color: #13a9bd; color: white; padding: 10px 20px; margin: 10px; border-radius: 5px; text-align: center;">
                Predicted High: ${st.session_state.high_pred:.2f}
            </div>
            <div style="background-color: #c92516; color: white; padding: 10px 20px; margin: 10px; border-radius: 5px; text-align: center;">
                Predicted Low: ${st.session_state.low_pred:.2f}
            </div>
        </div>
    """, unsafe_allow_html=True)

    daily_plots = plot_daily_data(bitcoinDataPipeline, start_date, end_date)
    
    for i in range(0, len(daily_plots), 2):
        cols = st.columns(2)
        for col, plot in zip(cols, daily_plots[i:i+2]):
            col.plotly_chart(plot, use_container_width=True)

if 'last_refresh_time' not in st.session_state:
    st.session_state.last_refresh_time = current_time

if (current_time - st.session_state.last_refresh_time).seconds > 3600:
    st.session_state.last_refresh_time = current_time
    st.rerun()

### Streamlit layout settings
st.markdown(
    """
    <style>
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 3rem;  /* Add some space for the footer */
    }
    .stApp {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
    }
    h1, h2, h3 {
        text-align: center;
    }
    .footer {
        width: 100%;
        background-color: #333;
        color: #f0f0f0;
        text-align: center;
        padding: 10px 0;
        position: relative;
        bottom: 0;
        left: 0;
        margin-top: 3rem;  /* Add some space above the footer */
    }
    </style>
    """,
    unsafe_allow_html=True
)

### Footer
st.markdown(
    """
    <div class="footer">
        <p><strong>Disclaimer:</strong> The information provided on this website is for informational purposes only and is not intended as financial advice. Always do your own research before making any investment decisions.</p>
        <p>Developed By Zeeshan Hameed</p>
    </div>
    """,
    unsafe_allow_html=True
)

