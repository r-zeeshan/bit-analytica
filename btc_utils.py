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

