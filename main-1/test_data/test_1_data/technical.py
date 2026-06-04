import pandas as pd
import numpy as np
import requests
from alpha_vantage.timeseries import TimeSeries
import yfinance as yf
from datetime import datetime, timedelta
import time
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def technical(symbol, key = "F1UXC7ZGHIEUFHUN", interval = "5min", output_size = "full"):
    url = f"https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_INTRADAY",
        "symbol": symbol,
        "interval": interval,
        "apikey": key,
        "outputsize": output_size,
    }

    response = requests.get(url, params=params)

    data = response.json()

    if f"Time Series ({interval})" in data:
        time_series = data[f"Time Series ({interval})"]
        df = pd.DataFrame.from_dict(time_series, orient="index", dtype=float)
        df.index = pd.to_datetime(df.index)
        df.sort_index(inplace=True)  # Ensure chronological order

        df.columns = ["open", "high", "low", "close", "volume"]
    else:
        print("Error:", data.get("Note", data.get("Error Message", "Unknown issue with the API request.")))
    filtered_data = df

    def calculate_rsi(series, period=14):
        delta = series.diff(1)
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        avg_gain = gain.rolling(window=period, min_periods=1).mean()
        avg_loss = loss.rolling(window=period, min_periods=1).mean()

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def process_data(df):
        """
        Process the input DataFrame to calculate %Close and update all indicators accordingly.
        """
        df['5. volume'] = df['volume']
        df['2. high'] = df['high']
        df['1. open '] = df['open']
        df['3. low'] = df['low']
        # Convert necessary columns to numeric types
        df['High'] = df['high']
        df['Low'] = df['low']

        # Calculate True Range (TR)
        df['prev_close'] = df['Close'].shift(1)
        df['tr'] = np.maximum(df['High'] - df['Low'],
                          np.maximum(abs(df['High'] - df['prev_close']),
                                     abs(df['Low'] - df['prev_close'])))

        # Calculate Directional Movement (+DM, -DM)
        df['+dm'] = np.where((df['High'] - df['High'].shift(1)) > (df['Low'].shift(1) - df['Low']),
                         np.maximum(df['High'] - df['High'].shift(1), 0), 0)
        df['-dm'] = np.where((df['Low'].shift(1) - df['Low']) > (df['High'] - df['High'].shift(1)),
                         np.maximum(df['Low'].shift(1) - df['Low'], 0), 0)

        # Smooth the True Range, +DM, and -DM (using rolling mean)
        period = 14
        df['atr'] = df['tr'].rolling(window=period).mean()
        df['+dm_smooth'] = df['+dm'].rolling(window=period).mean()
        df['-dm_smooth'] = df['-dm'].rolling(window=period).mean()

        # Calculate +DI and -DI
        df['+di'] = (df['+dm_smooth'] / df['atr']) * 100
        df['-di'] = (df['-dm_smooth'] / df['atr']) * 100

        # Calculate DX
        df['dx'] = (abs(df['+di'] - df['-di']) / (df['+di'] + df['-di'])) * 100

        # Calculate ADX (Smoothed DX)
        df['adx'] = df['dx'].rolling(window=period).mean()

        # Trend and Trend Strength
        df['Trend'] = np.where(df['+di'] > df['-di'], 1, 0)  # 1 = Upward, 0 = Downward
        df['Trend Strength'] = np.where(df['adx'] > 25, 1,  # Strong
                                     np.where(df['adx'] < 20, 0,  # Weak
                                              0.5))  # Moderate

        # Drop intermediate columns for clarity
        df = df.drop(columns=['prev_close', 'tr', '+dm', '-dm', '+dm_smooth', '-dm_smooth', 'dx'])

        # Calculate RSI using %Close
        df['RSI'] = calculate_rsi(df['4. close'], period=14)

        # Calculate Moving Averages
        df['MA_5'] = df['4. close'].rolling(window=5).mean()
        df['MA_10'] = df['4. close'].rolling(window=10).mean()
        df['MA_20'] = df['4. close'].rolling(window=20).mean()

        # Exponential Moving Averages (EMAs)
        df['EMA_12'] = df['4. close'].ewm(span=12, adjust=False).mean()
        df['EMA_26'] = df['4. close'].ewm(span=26, adjust=False).mean()

        # Bollinger Bands
        df['SMA_20'] = df['4. close'].rolling(window=20).mean()
        df['BB_Upper'] = df['SMA_20'] + 2 * df['4. close'].rolling(window=20).std()
        df['BB_Lower'] = df['SMA_20'] - 2 * df['4. close'].rolling(window=20).std()

        # Stochastic Oscillator
        df['L14'] = df['4. close'].rolling(window=14).min()
        df['H14'] = df['4. close'].rolling(window=14).max()
        df['Stochastic'] = 100 * ((df['4. close'] - df['L14']) / (df['H14'] - df['L14']))
        columns_to_drop = ['High', 'Low', 'open', 'high', 'low', '4. close', 'volume']  # Replace with your column names
        df = df.drop(columns=columns_to_drop)
        df = df.dropna()
        return df

    df = process_data(filtered_data)
    return df

import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta

def technical_indicators(the_df):
    def calculate_rsi(series, period=14):
        delta = series.diff(1)
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        avg_gain = gain.rolling(window=period, min_periods=1).mean()
        avg_loss = loss.rolling(window=period, min_periods=1).mean()

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def process_data(df):
        
        
        # True Range (TR)
        df['prev_close'] = df['close'].shift(1)
        df['tr'] = np.maximum(df['high'] - df['low'],
                              np.maximum(abs(df['high'] - df['prev_close']),
                                         abs(df['low'] - df['prev_close'])))

        # Directional Movement (+DM, -DM)
        df['+dm'] = np.where((df['high'] - df['high'].shift(1)) > (df['low'].shift(1) - df['low']),
                             np.maximum(df['high'] - df['high'].shift(1), 0), 0)
        df['-dm'] = np.where((df['low'].shift(1) - df['low']) > (df['high'] - df['high'].shift(1)),
                             np.maximum(df['low'].shift(1) - df['low'], 0), 0)

        # Smoothed values
        period = 14
        df['atr'] = df['tr'].rolling(window=period).mean()
        df['+dm_smooth'] = df['+dm'].rolling(window=period).mean()
        df['-dm_smooth'] = df['-dm'].rolling(window=period).mean()

        # Directional Indicators (+DI, -DI)
        df['+di'] = (df['+dm_smooth'] / df['atr']) * 100
        df['-di'] = (df['-dm_smooth'] / df['atr']) * 100

        # DX & ADX
        df['dx'] = (abs(df['+di'] - df['-di']) / (df['+di'] + df['-di'])) * 100
        df['adx'] = df['dx'].rolling(window=period).mean()

        # Trend & Strength
        df['Trend'] = np.where(df['+di'] > df['-di'], 1, 0)
        df['Trend Strength'] = np.where(df['adx'] > 25, 1,  # Strong
                                        np.where(df['adx'] < 20, 0,  # Weak
                                                 0.5))  # Moderate

        # Drop unnecessary columns
        df.drop(columns=['prev_close', 'tr', '+dm', '-dm', '+dm_smooth', '-dm_smooth', 'dx'], inplace=True)

        # RSI
        df['RSI'] = calculate_rsi(df['close'], period=14)

        # Moving Averages
        df['MA_5'] = df['close'].rolling(window=5).mean()
        df['MA_10'] = df['close'].rolling(window=10).mean()
        df['MA_20'] = df['close'].rolling(window=20).mean()

        # Exponential Moving Averages
        df['EMA_12'] = df['close'].ewm(span=12, adjust=False).mean()
        df['EMA_26'] = df['close'].ewm(span=26, adjust=False).mean()

        # Bollinger Bands
        df['SMA_20'] = df['close'].rolling(window=20).mean()
        df['BB_Upper'] = df['SMA_20'] + 2 * df['close'].rolling(window=20).std()
        df['BB_Lower'] = df['SMA_20'] - 2 * df['close'].rolling(window=20).std()

        # Stochastic Oscillator
        df['L14'] = df['close'].rolling(window=14).min()
        df['H14'] = df['close'].rolling(window=14).max()
        df['Stochastic'] = 100 * ((df['close'] - df['L14']) / (df['H14'] - df['L14']))

        # Drop unnecessary columns
        df.drop(columns=['L14', 'H14'], inplace=True)
        df.dropna(inplace=True)
        return df
    df = the_df.copy() 
    #df.rename(columns={'Timestamp': 'timestamp', 'Volume': 'volume', 'High': 'high', 'Open': 'open', 'Close': 'close', 'Low': 'low'}, inplace=True)
    df = process_data(df)
    df.set_index('timestamp', inplace=True, drop=False)
    df.drop(columns=['timestamp'], inplace=True)
    return df


def technical_polygon(symbol, api_key="LTikapZvdZjraWfVP2r_QgAvTX_oZSZw", start_date=None, end_date=None, order="desc", days=30, interval_range=15, interval="minute"):
    def calculate_rsi(series, period=14):
        delta = series.diff(1)
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        avg_gain = gain.rolling(window=period, min_periods=1).mean()
        avg_loss = loss.rolling(window=period, min_periods=1).mean()

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def process_data(df):
        """
        Process the input DataFrame to calculate indicators.
        """
        # Ensure numeric types
        df[['open', 'high', 'low', 'close', 'volume']] = df[['open', 'high', 'low', 'close', 'volume']].astype(float)

        # True Range (TR)
        df['prev_close'] = df['close'].shift(1)
        df['tr'] = np.maximum(df['high'] - df['low'],
                              np.maximum(abs(df['high'] - df['prev_close']),
                                         abs(df['low'] - df['prev_close'])))

        # Directional Movement (+DM, -DM)
        df['+dm'] = np.where((df['high'] - df['high'].shift(1)) > (df['low'].shift(1) - df['low']),
                             np.maximum(df['high'] - df['high'].shift(1), 0), 0)
        df['-dm'] = np.where((df['low'].shift(1) - df['low']) > (df['high'] - df['high'].shift(1)),
                             np.maximum(df['low'].shift(1) - df['low'], 0), 0)

        # Smoothed values
        period = 14
        df['atr'] = df['tr'].rolling(window=period).mean()
        df['+dm_smooth'] = df['+dm'].rolling(window=period).mean()
        df['-dm_smooth'] = df['-dm'].rolling(window=period).mean()

        # Directional Indicators (+DI, -DI)
        df['+di'] = (df['+dm_smooth'] / df['atr']) * 100
        df['-di'] = (df['-dm_smooth'] / df['atr']) * 100

        # DX & ADX
        df['dx'] = (abs(df['+di'] - df['-di']) / (df['+di'] + df['-di'])) * 100
        df['adx'] = df['dx'].rolling(window=period).mean()

        # Trend & Strength
        df['Trend'] = np.where(df['+di'] > df['-di'], 1, 0)
        df['Trend Strength'] = np.where(df['adx'] > 25, 1,  # Strong
                                        np.where(df['adx'] < 20, 0,  # Weak
                                                 0.5))  # Moderate

        # Drop unnecessary columns
        df.drop(columns=['prev_close', 'tr', '+dm', '-dm', '+dm_smooth', '-dm_smooth', 'dx'], inplace=True)

        # RSI
        df['RSI'] = calculate_rsi(df['close'], period=14)

        # Moving Averages
        df['MA_5'] = df['close'].rolling(window=5).mean()
        df['MA_10'] = df['close'].rolling(window=10).mean()
        df['MA_20'] = df['close'].rolling(window=20).mean()

        # Exponential Moving Averages
        df['EMA_12'] = df['close'].ewm(span=12, adjust=False).mean()
        df['EMA_26'] = df['close'].ewm(span=26, adjust=False).mean()

        # Bollinger Bands
        df['SMA_20'] = df['close'].rolling(window=20).mean()
        df['BB_Upper'] = df['SMA_20'] + 2 * df['close'].rolling(window=20).std()
        df['BB_Lower'] = df['SMA_20'] - 2 * df['close'].rolling(window=20).std()

        # Stochastic Oscillator
        df['L14'] = df['close'].rolling(window=14).min()
        df['H14'] = df['close'].rolling(window=14).max()
        df['Stochastic'] = 100 * ((df['close'] - df['L14']) / (df['H14'] - df['L14']))

        # Drop unnecessary columns
        df.drop(columns=['L14', 'H14'], inplace=True)
        df.dropna(inplace=True)
        return df

    # Set date range if not provided
    if start_date is None:
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    if end_date is None:
        end_date = datetime.now().strftime('%Y-%m-%d')

    # API Request
    url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/{interval_range}/{interval}/{start_date}/{end_date}?adjusted=true&sort={order}&limit=50000&apiKey={api_key}"
    
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        if 'results' in data:
            df = pd.DataFrame(data['results'])
            df['t'] = pd.to_datetime(df['t'], unit='ms')

            df.rename(columns={'t': 'timestamp', 'v': 'volume', 'h': 'high', 'o': 'open', 'c': 'close', 'l': 'low'}, inplace=True)
            df.drop(columns=['n', 'vw'], errors='ignore', inplace=True)

            df = process_data(df)
            df.set_index('timestamp', inplace=True, drop=False)
            df.drop(columns=['timestamp'], inplace=True)
            return df

    return pd.DataFrame()  # Return empty DataFrame if API fails

    
def update_nvda_full():
    # Alpha Vantage API key and symbol configuration
    api_key = 'F1UXC7ZGHIEUFHUN'
    symbol = 'NVDA'

    # Read the existing data and rename the timestamp column
    file_path = r'C:\Users\david\OneDrive\Desktop\fin_data\stock_data\nvda_1min_full.xlsx'
    df_existing = pd.read_excel(file_path).rename(columns={'Unnamed: 0': 'timestamp'})

    print(df_existing.dtypes)

    # Get the latest timestamp in the current DataFrame
    last_timestamp = pd.to_datetime(df_existing['timestamp']).max()

    # Fetch new data from Alpha Vantage
    ts = TimeSeries(key=api_key, output_format='pandas')
    data, meta_data = ts.get_intraday(symbol=symbol, interval='1min', outputsize='full')

    # Format and clean the Alpha Vantage DataFrame
    data.reset_index(inplace=True)
    data.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    data['timestamp'] = pd.to_datetime(data['timestamp'])

    # Filter for new rows only
    new_data = data[data['timestamp'] > last_timestamp]

    if not new_data.empty:
        # Append the new data and sort by timestamp
        updated_df = pd.concat([df_existing, new_data], ignore_index=True)
        updated_df.sort_values('timestamp', inplace=True)
        
        # Save the updated data back to Excel
        updated_df.to_excel(file_path, index=False)
        print("Data successfully updated and saved.")
    else:
        print("No new data available.")

import requests
import pandas as pd
from datetime import datetime, timedelta

def get_stock_open_prices(ticker: str, dates: list, api_key='6FScTtPXo3hC4lyzkRb29mNJOOmLYwYF') -> list:
    """
    Fetches the open prices of a stock for a list of dates using Polygon API.
    If a date falls on a non-trading day, it backfills with the closest available trading day's price (past or future).

    Args:
        ticker (str): Stock ticker symbol (e.g., "NVDA").
        dates (list): List of dates (strings in "YYYY-MM-DD" format).
        api_key (str): Polygon API key.

    Returns:
        list: Open prices corresponding to the input dates (backfilled for closed market days).
    """
    # Convert string dates to datetime objects
    date_objs = [datetime.strptime(date, "%Y-%m-%d") for date in dates]
    
    # Find the earliest and latest date to fetch data efficiently
    start_date = min(date_objs).strftime("%Y-%m-%d")
    end_date = max(date_objs).strftime("%Y-%m-%d")

    # Polygon Aggregates API URL (1-day interval)
    url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{start_date}/{end_date}?adjusted=true&apiKey={api_key}"
    
    try:
        response = requests.get(url)
        data = response.json()

        # Check if the response contains valid results
        if "results" not in data:
            print(f"⚠️ No data found for {ticker}. Check API key or date range.")
            return [None] * len(dates)

        # Convert API response to a dictionary {date: open_price}
        price_dict = {datetime.utcfromtimestamp(d['t'] / 1000).strftime("%Y-%m-%d"): d['o'] for d in data['results']}

        # ✅ Backfilling: Ensure every requested date gets a valid open price
        sorted_dates = sorted(price_dict.keys())

        # **Ensure all input dates get a valid open price**
        open_prices = []
        for date in dates:
            if date in price_dict:
                open_prices.append(price_dict[date])  # Use exact match
            else:
                # **Find the closest past date**
                past_dates = [d for d in sorted_dates if d < date]
                closest_past_date = past_dates[-1] if past_dates else None

                # **Find the closest future date**
                future_dates = [d for d in sorted_dates if d > date]
                closest_future_date = future_dates[0] if future_dates else None

                # **Choose the closest available date (past or future)**
                if closest_past_date and closest_future_date:
                    past_diff = abs((datetime.strptime(date, "%Y-%m-%d") - datetime.strptime(closest_past_date, "%Y-%m-%d")).days)
                    future_diff = abs((datetime.strptime(closest_future_date, "%Y-%m-%d") - datetime.strptime(date, "%Y-%m-%d")).days)

                    # Pick the closest of the two
                    chosen_date = closest_past_date if past_diff <= future_diff else closest_future_date
                else:
                    chosen_date = closest_past_date or closest_future_date  # Pick whichever exists

                open_prices.append(price_dict.get(chosen_date, None))  # Use chosen date

        return open_prices

    except requests.RequestException as e:
        print(f"⚠️ API Request Error: {e}")
        return [None] * len(dates)