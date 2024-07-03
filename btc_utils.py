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
