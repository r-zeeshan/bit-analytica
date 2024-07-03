import pandas as pd

def calculate_sma(data, window):
    """
    Calculate the Simple Moving Average (SMA) for a given data set.

    Parameters:
    - data: Pandas DataFrame containing the data set.
    - window: Integer representing the window size for the moving average calculation.

    Returns:
    - sma: Pandas Series representing the Simple Moving Average.
    """
    sma = data['Close'].rolling(window=window).mean()
    return sma


def calculate_ema(data, window):
    """
    Calculate the Exponential Moving Average (EMA) of the 'Close' prices in the given data.

    Parameters:
    - data: A pandas DataFrame containing the 'Close' prices.
    - window: An integer specifying the window size for the EMA calculation.

    Returns:
    - ema: A pandas Series representing the EMA values.
    """
    ema = data['Close'].ewm(span=window, adjust=False).mean()
    return ema


def calculate_rsi(data, window=14):
    """
    Calculate the Relative Strength Index (RSI) for a given dataset.

    Parameters:
    - data: pandas DataFrame or Series containing the 'Close' prices.
    - window: int, optional (default=14)
        The number of periods to use for the RSI calculation.

    Returns:
    - rsi: pandas Series
        The calculated RSI values.

    """
    delta = data['Close'].diff()
    gain = (delta.where(delta>0, 0)).rolling(window=window).mean()
    loss = (delta.where(delta<0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculat_macd(data, short_window=12, long_window=26, signal_window=9):
    """
    Calculate the Moving Average Convergence Divergence (MACD) indicator.

    Parameters:
    - data: The input data for calculating MACD.
    - short_window: The window size for the short-term exponential moving average (default: 12).
    - long_window: The window size for the long-term exponential moving average (default: 26).
    - signal_window: The window size for the signal line exponential moving average (default: 9).

    Returns:
    - A DataFrame containing the MACD and Signal Line values.
    """
    short_ema = calculate_ema(data, short_window)
    long_ema = calculate_ema(data, long_window)
    macd = short_ema - long_ema 
    signal = macd.ewm(span=signal_window, adjust=False).mean()
    return pd.DataFrame({'MACD':macd, 'Signal Line':signal})


def calculate_bollinger_bands(data, window=20, num_std=2):
    sma = calculate_sma(data, window)
    rolling_std = data['Close'].rolling(window=window).std()
    upper_band = sma + (rolling_std * num_std)
    lower_band = sma - (rolling_std * num_std)
    return pd.DataFrame({
        "Bollinger_SMA": sma,
        "Upper_Band" : upper_band,
        "Lower_Bank" : lower_band, 
    })


def calculate_atr(data, window=14):
    """
    Calculate the Average True Range (ATR) for a given dataset.

    Parameters:
    - data: pandas DataFrame containing the necessary columns ('High', 'Low', 'Close').
    - window: int, optional (default=14). The window size for calculating the rolling mean.

    Returns:
    - atr: pandas Series containing the calculated Average True Range values.

    """
    high_low = data['High'] - data['Low']
    high_close = (data['High'] - data['Close'].shift()).abs()
    low_close = (data['Low'] - data['Close'].shift()).abs()
    true_range = high_low.combine(high_close, max).combine(low_close, max)
    atr = true_range.rolling(window=window).mean()
    return atr


def calculate_stochastic_oscillator(data, window=14):
    """
    Calculate the Stochastic Oscillator for a given dataset.

    Args:
        data (pandas.DataFrame): The input dataset containing 'low', 'High', and 'Close' columns.
        window (int): The window size for calculating the rolling minimum and maximum values. Default is 14.

    Returns:
        pandas.DataFrame: A DataFrame containing the '%K' and '%D' columns.

    """
    low_min = data['low'].rolling(window=window).min()
    high_max = data['High'].rolling(window=window).max()
    data['%K'] = 100 * ((data['Close']- low_min) / (high_max - low_min))
    data['%D'] = data['%K'].rolling(window=3).mean()
    return data[['%K', '%D']]


def calculate_obv(data):
    """
    Calculate the On-Balance Volume (OBV) for the given data.

    Parameters:
    data (pandas.DataFrame): The input data containing 'Volume' and 'Close' columns.

    Returns:
    pandas.Series: The calculated On-Balance Volume (OBV) values.
    """
    obv = (data['Volume'] * ((data['Close'] > data['Close'].shift()).astype(int) - 
                             (data['Close'] < data['Close'].shift()).astype(int))).cumsum()
    return obv
