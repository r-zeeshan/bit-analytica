import streamlit as st
from datetime import datetime, timedelta
import pytz
from text_data_pipeline import TextDataPipeline
from btc_data_pipeline import BitcoinDataPipeline
from config import LLM
from app_utils import load_models, getData, predict_price
from plot_utils import plot_all_indicators, plot_with_sma_or_ema, plot_with_rsi

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
    with st.spinner("Getting sentiment score..."):
        data = getData(textDataPipeline, bitcoinDataPipeline, x_scaler)
    
    with st.spinner("Predicting high price..."):
        high_pred = predict_price(high_model, data, y_high_scaler, flag=True)
    
    with st.spinner("Predicting low price..."):
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
    # Create placeholders for the initial run
    st.session_state.high_pred = None
    st.session_state.low_pred = None

# Create two columns for layout
col1, col2 = st.columns([8, 2])

# Plot the hourly data chart in the left column
with col1:
    st.subheader("Bitcoin Hourly Data with Technical Indicators")
    fig = plot_hourly_data(bitcoinDataPipeline)
    st.plotly_chart(fig, use_container_width=True)

# Display predictions on the right column
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
        
        high_pred, low_pred = update_predictions(
            textDataPipeline, bitcoinDataPipeline, x_scaler, high_model, y_high_scaler, low_model, y_low_scaler
        )
        
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

# Get the current time
current_time = datetime.now(timezone)

# Check if it's time to update the predictions (every 24 hours at 7 AM UTC-4)
if current_time.hour == 7 and current_time.minute == 0:
    high_pred, low_pred = update_predictions(
        textDataPipeline, bitcoinDataPipeline, x_scaler, high_model, y_high_scaler, low_model, y_low_scaler
    )
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
    </style>
    """,
    unsafe_allow_html=True
)

# Plot three additional charts below the main columns
st.markdown("---")

chart_col1, chart_col2, chart_col3 = st.columns(3)
start_date = datetime.now().strftime('%Y-%m-%d')
end_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
with chart_col1:
    st.subheader("SMA7")
    sma7_fig = plot_with_sma_or_ema(bitcoinDataPipeline.getHourlyData(), start_date, end_date, 'SMA_7')
    st.plotly_chart(sma7_fig, use_container_width=True)

with chart_col2:
    st.subheader("EMA7")
    ema7_fig = plot_with_sma_or_ema(bitcoinDataPipeline.getHourlyData(), start_date, end_date, 'EMA_7')
    st.plotly_chart(ema7_fig, use_container_width=True)

with chart_col3:
    st.subheader("RSI")
    rsi_fig = plot_with_rsi(bitcoinDataPipeline.getHourlyData(), start_date, end_date, 'RSI')
    st.plotly_chart(rsi_fig, use_container_width=True)
