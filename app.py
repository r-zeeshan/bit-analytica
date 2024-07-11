import streamlit as st
from datetime import datetime, timedelta
import pytz
from text_data_pipeline import TextDataPipeline
from btc_data_pipeline import BitcoinDataPipeline
from config import LLM
from app_utils import load_models, getData, predict_price
from plot_utils import plot_all_indicators


@st.cache_resource
def initialize_pipelines_and_models():
    # Initialize pipelines
    textDataPipeline = TextDataPipeline(LLM)
    bitcoinDataPipeline = BitcoinDataPipeline()

    # Load models and scalers
    x_scaler, y_high_scaler, y_low_scaler, high_model, low_model = load_models()
    
    return textDataPipeline, bitcoinDataPipeline, x_scaler, y_high_scaler, y_low_scaler, high_model, low_model


def plot_hourly_data(bitcoinDataPipeline):
    hourly_data = bitcoinDataPipeline.getHourlyData()
    start_date = (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')
    fig = plot_all_indicators(hourly_data, start_date, end_date)
    return fig


def update_predictions(textDataPipeline, bitcoinDataPipeline, x_scaler, high_model, y_high_scaler, low_model, y_low_scaler):
    data = getData(textDataPipeline, bitcoinDataPipeline, x_scaler)
    high_pred = predict_price(high_model, data, y_high_scaler, flag=True)
    low_pred = predict_price(low_model, data, y_low_scaler, flag=False)
    return high_pred, low_pred


# Define timezone
timezone = pytz.timezone("America/New_York")

# Set Streamlit page configuration
st.set_page_config(layout="wide", page_title="BitAnalytica")

# Title of the application
st.title("BitAnalytica")

# Initialize pipelines and models
textDataPipeline, bitcoinDataPipeline, x_scaler, y_high_scaler, y_low_scaler, high_model, low_model = initialize_pipelines_and_models()

# Initialize predictions with default values
if 'high_pred' not in st.session_state or 'low_pred' not in st.session_state:
    st.session_state.high_pred, st.session_state.low_pred = update_predictions(
        textDataPipeline, bitcoinDataPipeline, x_scaler, high_model, y_high_scaler, low_model, y_low_scaler
    )

# Get the current time
current_time = datetime.now(timezone)

# Check if it's time to update the predictions (every 24 hours at 7 AM UTC-4)
if current_time.hour == 7 and current_time.minute == 0:
    st.session_state.high_pred, st.session_state.low_pred = update_predictions(
        textDataPipeline, bitcoinDataPipeline, x_scaler, high_model, y_high_scaler, low_model, y_low_scaler
    )

# Plot the hourly data chart
with st.container():
    st.subheader("Bitcoin Hourly Data with Technical Indicators")
    fig = plot_hourly_data(bitcoinDataPipeline)
    st.plotly_chart(fig, use_container_width=True)

# Display predictions on the right side
with st.container():
    st.subheader("Predictions")
    st.write(f"Predicted High: ${st.session_state.high_pred:.2f}")
    st.write(f"Predicted Low: ${st.session_state.low_pred:.2f}")

# Auto-refresh the chart every hour
if 'last_refresh_time' not in st.session_state:
    st.session_state.last_refresh_time = current_time

if (current_time - st.session_state.last_refresh_time).seconds > 3600:
    st.session_state.last_refresh_time = current_time
    st.rerun()

# Streamlit layout settings
st.markdown(
    """
    <style>
    .main .block-container {
        padding-top: 1rem;
    }
    .stApp {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
    }
    .stPlotlyChart {
        width: 80%;
    }
    .stMarkdown {
        width: 20%;
    }
    </style>
    """,
    unsafe_allow_html=True
)
