import streamlit as st
from datetime import datetime, timedelta
import pytz
from text_data_pipeline import TextDataPipeline
from btc_data_pipeline import BitcoinDataPipeline
from config import LLM
from app_utils import load_models, getData, predict_price
from plot_utils import plot_all_indicators, plot_with_sma, plot_with_ema, plot_with_rsi, plot_with_macd, plot_with_bollinger_bands, plot_with_atr, plot_with_stochastic, plot_with_obv

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
    start_date = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
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


def plot_daily_data(bitcoinDataPipeline, start_date, end_date):
    daily_data = bitcoinDataPipeline.getLatestBitcoinData()
    plots = []
    plots.append(plot_with_sma(daily_data, start_date, end_date, 'SMA_7', 'SMA_14'))
    plots.append(plot_with_ema(daily_data, start_date, end_date, 'EMA_7', 'EMA_14'))
    plots.append(plot_with_rsi(daily_data, start_date, end_date, 'RSI'))
    plots.append(plot_with_macd(daily_data, start_date, end_date, 'MACD', 'Signal Line'))
    plots.append(plot_with_bollinger_bands(daily_data, start_date, end_date, 'Bollinger_SMA', 'Upper_Band_BB', 'Lower_Band_BB'))
    plots.append(plot_with_atr(daily_data, start_date, end_date, 'ATR'))
    plots.append(plot_with_stochastic(daily_data, start_date, end_date, '%K', '%D'))
    plots.append(plot_with_obv(daily_data, start_date, end_date, 'OBV'))
    return plots


# Define timezone
timezone = pytz.timezone("America/New_York")

# Set Streamlit page configuration
st.set_page_config(layout="wide", page_title="BitAnalytica")

# Title
st.markdown(
    """
    <div style="text-align: center; padding-top: 100px;">
        <h1>BitAnalytica</h1>
    </div>
    """,
    unsafe_allow_html=True
)

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
    st.markdown(
        """
        <div style="text-align: center; justify-content: center">
            <h3>Bitcoin Hourly Data with Technical Indicators</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
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

# Initial plotting of daily charts
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

    # Update the daily charts
    daily_plots = plot_daily_data(bitcoinDataPipeline, start_date, end_date)
    
    # Plot each technical indicator chart in a grid layout
    for i in range(0, len(daily_plots), 2):
        cols = st.columns(2)
        for col, plot in zip(cols, daily_plots[i:i+2]):
            col.plotly_chart(plot, use_container_width=True)

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
    footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #f0f0f0;
        color: black;
        text-align: center;
        padding: 10px 0;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Footer
st.markdown(
    """
    <footer>
        <p><strong>Disclaimer:</strong> The information provided on this website is for informational purposes only and is not intended as financial advice. Always do your own research before making any investment decisions.</p>
        <p>Developed By Zeeshan Hameed</p>
    </footer>
    """,
    unsafe_allow_html=True
)
