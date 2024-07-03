import plotly.graph_objects as go


TEMPLATE = 'plotly_dark'

def add_candlestick_trace(fig, data):
    """
    Adds a candlestick trace to the given figure.

    Parameters:
    - fig (plotly.graph_objects.Figure): The figure to add the trace to.
    - data (pandas.DataFrame): The data containing the candlestick values.

    Returns:
    None
    """
    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name="Candlestick"
    ))



def plot_with_sma_or_ema(data, start_date, end_date, column):
    """
    Plots a candlestick chart with a line plot of a specific column (SMA or EMA) for a given date range.

    Args:
        data (pandas.DataFrame): The data containing the candlestick and line plot data.
        start_date (str): The start date of the date range.
        end_date (str): The end date of the date range.
        column (str): The column name to plot as a line plot.

    Returns:
        go.Figure: The plotly figure object containing the candlestick chart and line plot.
    """
    data = data.loc[start_date:end_date]

    fig = go.Figure()
    add_candlestick_trace(fig, data)

    fig.add_trace(go.Scatter(
        x=data.index,
        y=data[column],
        modes='lines',
        name=column   
    ))

    fig.update_layout(
        title=f"Bitcoin Candlestick with {column}",
        yaxis_title='Price (USD)',
        xaxis_title='Date',
        template=TEMPLATE
    )

    return fig


def plot_with_rsi(data, start_date, end_date, column):
    """
    Plots a candlestick chart with a specified column and RSI (Relative Strength Index) overlay.

    Args:
        data (pandas.DataFrame): The data containing the candlestick and column data.
        start_date (str): The start date of the data to be plotted.
        end_date (str): The end date of the data to be plotted.
        column (str): The column name to be plotted on the secondary y-axis.

    Returns:
        go.Figure: The plotted figure.

    """
    data = data.loc[start_date:end_date]

    fig = go.Figure()
    add_candlestick_trace(fig, data)

    fig.add_trace(go.Scatter(
        x=data.index,
        y=data[column],
        mode='lines',
        name=column,
        yaxis='y2'
    ))

    fig.update_layout(
        title=f'Bitcoin Candlestick with {column}',
        yaxis_title="Price (USD)",
        xaxis_title="Date",
        template=TEMPLATE,
        yaxis2=dict(
            title='RSI',
            overlaying='y',
            side='right',
            range=[0, 100]
        )
    )

    return fig


def plot_with_macd(data, start_date, end_date, macd_column, signal_column):
    """
    Plots a candlestick chart of Bitcoin prices with MACD and signal lines.

    Args:
        data (pandas.DataFrame): The data containing Bitcoin prices.
        start_date (str): The start date for the plot.
        end_date (str): The end date for the plot.
        macd_column (str): The column name for the MACD line in the data.
        signal_column (str): The column name for the signal line in the data.

    Returns:
        go.Figure: The plotly figure object containing the candlestick chart with MACD and signal lines.
    """
    data = data.loc[start_date:end_date]

    fig = go.Figure()
    add_candlestick_trace(fig, data)

    fig.add_trace(go.Scatter(
        x=data.index,
        y=data[macd_column], ### MACD LINE
        mode='lines',
        name=macd_column
    ))

    fig.add_trace(go.Scatter(
        x=data.index,
        y=data[signal_column], ### SIGNAL LINE
        mode='lines',
        name=signal_column
    ))

    fig.update_layout(
        title=f'Bitcoin Candlestick with {macd_column} and {signal_column}',
        yaxis_title='Price (USD)',
        xaxis_title='Date',
        template=TEMPLATE
    )

    return fig


def plot_with_bollinger_bands(data, start_date, end_date, sma_column, upper_band, lower_band):
    """
    Plots a candlestick chart with Bollinger Bands.

    Args:
        data (pandas.DataFrame): The data containing the candlestick chart data.
        start_date (str): The start date for the plot.
        end_date (str): The end date for the plot.
        sma_column (str): The column name for the Simple Moving Average (SMA) line.
        upper_band (str): The column name for the Upper Bollinger Band line.
        lower_band (str): The column name for the Lower Bollinger Band line.

    Returns:
        plotly.graph_objects.Figure: The plotted figure.
    """
    data = data.loc[start_date:end_date]

    fig = go.Figure()
    add_candlestick_trace(fig, data)

    fig.add_trace(go.Scatter(
        x=data.index,
        y=data[sma_column], ### SMA LINE
        mode='lines',
        name=sma_column
    ))

    fig.add_trace(go.Scatter(
        x=data.index,
        y=data[upper_band], ### Upper Bollinger Band Line
        mode="lines",
        name=upper_band
    ))

    fig.add_trace(go.Scatter(
        x=data.index,
        y=data[lower_band], ### Lower Bollinger Band Line
        mode="lines",
        name=lower_band
    ))

    fig.update_layout(
        title=f'Bitcoin Candlestick with Bollinger Bands ({sma_column}, {upper_band}, {lower_band})',
        yaxis_title='Price (USD)',
        xaxis_title='Date',
        template=TEMPLATE
    )

    return fig


def plot_with_atr(data, start_date, end_date, column):
    """
    Plots a Bitcoin candlestick chart with a specified column.

    Args:
        data (pandas.DataFrame): The data containing the Bitcoin candlestick data.
        start_date (str): The start date for the plot.
        end_date (str): The end date for the plot.
        column (str): The column to be plotted.

    Returns:
        plotly.graph_objects.Figure: The plotted figure.
    """
    data = data.loc[start_date:end_date]

    fig = go.Figure(go.Scatter(
        x=data.index,
        y=data[column],
        mode='lines',
        name=column,
        yaxis='y2'
    ))

    fig.update_layout(
        title=f'Bitcoin Candlestick with {column}',
        yaxis_title='Price (USD)',
        xaxis_title='Date',
        template=TEMPLATE,
        yaxis2=dict(
            title='ATR',
            overlaying='y',
            side='right'
        )
    )

    return fig


def plot_with_stochastic(data, start_date, end_date, k_column, d_column):
    """
    Plots a candlestick chart with the Stochastic Oscillator (%K and %D) overlay.

    Args:
        data (pandas.DataFrame): The data containing the candlestick chart data.
        start_date (str): The start date for the data to be plotted.
        end_date (str): The end date for the data to be plotted.
        k_column (str): The column name for the %K line data.
        d_column (str): The column name for the %D line data.

    Returns:
        plotly.graph_objects.Figure: The figure object representing the candlestick chart with the Stochastic Oscillator overlay.
    """
    data = data.loc[start_date:end_date]

    fig = go.Figure()
    add_candlestick_trace(fig, data)

    fig.add_trace(go.Scatter(
        x=data.index,
        y=data[k_column], ### %K Line
        mode='lines',
        name=k_column,
        yaxis='y2'
    ))

    fig.add_trace(go.Scatter(
        x=data.index,
        y=data[d_column], ### %D Line
        mode='lines',
        name=d_column,
        yaxis='y2'
    ))

    fig.update_layout(
        title=f'Bitcoin Candlestick with Stochastic Oscillator (%K and %D)',
        yaxis_title='Price (USD)',
        xaxis_title='Date',
        template=TEMPLATE,
        yaxis2=dict(
            title='Stochastic Oscillator',
            overlaying='y',
            side='right',
            range=[0, 100]
        )
    )

    return fig


def plot_with_obv(data, start_date, end_date, column):
    """
    Plots a candlestick chart with On-Balance Volume (OBV) line.

    Args:
        data (pandas.DataFrame): The data containing the candlestick and OBV data.
        start_date (str): The start date for the data to be plotted.
        end_date (str): The end date for the data to be plotted.
        column (str): The column name for the OBV data.

    Returns:
        go.Figure: The figure object containing the candlestick chart with OBV line.
    """
    data = data.loc[start_date:end_date]

    fig = go.Figure()
    add_candlestick_trace(fig, data)

    fig.add_trace(go.Scatter(
        x=data.index,
        y=data[column], ### OBV Line
        mode='lines',
        name=column,
        yaxis='y2'
    ))

    fig.update_layout(
        title=f'Bitcoin Candlestick with {column}',
        yaxis_title='Price (USD)',
        xaxis_title='Date',
        template=TEMPLATE,
        yaxis2=dict(
            title='OBV',
            overlaying='y',
            side='right'
        )
    )

    return fig