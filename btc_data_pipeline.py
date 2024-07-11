from btc_utils import *
from config import *
from datetime import datetime, timedelta

class BitcoinDataPipeline:
    """
    A class that represents a Bitcoin data pipeline.

    This class retrieves the latest Bitcoin data from Yahoo Finance and calculates various technical indicators.

    Attributes:
        btc (pandas.DataFrame): Bitcoin data with calculated technical indicators.
    """

    def __init__(self):
        """
        Initializes a new instance of the BitcoinDataPipeline class.
        """
        self.btc = None


    def getLatestBitcoinData(self):
        """
        Retrieves the latest Bitcoin data from Yahoo Finance and calculates various technical indicators.

        Returns:
            pandas.DataFrame: Bitcoin data with calculated technical indicators.
        """
        data = get_data_from_yahoo(start='2016-12-01')
        data[SMA7] = calculate_sma(data, 7) ### Calculating SMA for 7 Days
        data[SMA14] = calculate_sma(data, 14) ### Calculating SMA for 14 Days
        data[EMA7] = calculate_ema(data, 7) ### Calculating EMA for 7 Days
        data[EMA14] = calculate_ema(data, 14) ### Calculating SMA for 14 Days
        data[RSI] = calculate_rsi(data, window=14) ### Calculating SMA for 14 Days
        data[[MACD, SIGNAL_LINE]] = calculat_macd(data, short_window=12, long_window=26, signal_window=9) ### Calculating MACD
        data[[BOLLINGER_SMA, UPPER_BAND_BB, LOWER_BAND_BB]] = calculate_bollinger_bands(data, window=20, num_std=2) ### Calculating Bollinger Bands
        data[ATR] = calculate_atr(data, window=14) ### Calculating ATR
        data[[K, D]] = calculate_stochastic_oscillator(data, window=14) ### Calculating Stochastic Oscillator
        data[OBV] = calculate_obv(data) ### Calculating OBV

        self.btc = data.loc['2017-01-08':]
        return self.btc
    

    def getHourlyData(self):
        """
        Retrieves hourly data for the past 14 days and calculates various technical indicators.

        Returns:
            pandas.DataFrame: A DataFrame containing the hourly data and calculated indicators.
        """
        end = datetime.now()
        start = end - timedelta(days=7)
        data = get_data_from_yahoo(start=start.strftime('%Y-%m-%d'), end=end.strftime('%Y-%m-%d'), interval='1h')
        data[SMA7] = calculate_sma(data, 7) ### Calculating SMA for 7 Hours
        data[SMA14] = calculate_sma(data, 14) ### Calculating SMA for 14 Hours
        data[EMA7] = calculate_ema(data, 7) ### Calculating EMA for 7 Hours
        data[EMA14] = calculate_ema(data, 14) ### Calculating SMA for 14 Hours
        data[RSI] = calculate_rsi(data, window=14) ### Calculating SMA for 14 Hours
        data[[MACD, SIGNAL_LINE]] = calculat_macd(data, short_window=12, long_window=26, signal_window=9) ### Calculating MACD
        data[[BOLLINGER_SMA, UPPER_BAND_BB, LOWER_BAND_BB]] = calculate_bollinger_bands(data, window=20, num_std=2) ### Calculating Bollinger Bands
        data[ATR] = calculate_atr(data, window=14) ### Calculating ATR
        data[[K, D]] = calculate_stochastic_oscillator(data, window=14) ### Calculating Stochastic Oscillator
        data[OBV] = calculate_obv(data) ### Calculating OBV

        return data

