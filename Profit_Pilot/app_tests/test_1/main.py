import pandas as pd
import numpy as np
from datetime import datetime, timedelta

forecasting_horizon = 10
input_chunk_length = 180
ticker = 'AAPL'
interval = "minute"
interval_range = 5
days = 100
time_slept = 60 * 2 # N minutes between checks
results_df = pd.DataFrame(columns=["Timestamp", "Buy_Signal", "Close"])
this_is_a_test = False
first_pred = True
port = 7497

import os
import re

from darts import TimeSeries
import joblib

import time
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

from sklearn.preprocessing import LabelEncoder

from darts.models.forecasting.tft_model import TFTModel
from darts.dataprocessing.transformers import Scaler
from darts.timeseries import TimeSeries

from news import scrape_insider_data, scrape_congress_trading_data, sentiment, get_zacks_rank
from fundamental import fundamental
from technical import get_stock_open_prices, technical_polygon, technical_indicators

from BuySell import buy, close_buy, disconnect, connect

insider_df = pd.DataFrame()
congress_df = pd.DataFrame()
sentiment_df = pd.DataFrame()
zacks_rank_df = pd.DataFrame()
fundamental_df = pd.DataFrame()
technical_df = pd.DataFrame()

os.makedirs(f"test_data\{ticker}", exist_ok=True)

insider_df = scrape_insider_data(ticker)
print('congress')
congress_df = scrape_congress_trading_data(ticker)
print('sentiment')
sentiment_df = sentiment([ticker])
print('zacks')
zacks_rank = get_zacks_rank(ticker)
zacks_rank_df = pd.DataFrame({"Zacks_Rank": [zacks_rank]})
print('fundamental')
fundamental_score_df = fundamental(ticker)
# Save each dataframe to CSV for further use
insider_df.to_csv(f"test_data\{ticker}\{ticker}_Insider_Trading.csv", index=False)
print('congress')
congress_df.to_csv(f"test_data\{ticker}\{ticker}_Congress_Trades.csv", index=False)
print('sentiment')
#sentiment_df.to_csv(f"test_data\{ticker}\{ticker}_Sentiment_Data.csv", index=False)
print('zacks')
zacks_rank_df.to_csv(f"test_data\{ticker}\{ticker}_Zacks_Rank.csv", index=False)
print('fundamental')
fundamental_score_df.to_csv(f"test_data\{ticker}\{ticker}_Fundamental_Score.csv", index=False)

import pandas as pd
import re

# Load data
insider_df = pd.read_csv(f"test_data/{ticker}/{ticker}_Insider_Trading.csv")
congress_df = pd.read_csv(f"test_data/{ticker}/{ticker}_Congress_Trades.csv")

# Convert date columns to standardized YYYY-MM-DD format
date_columns = ['Disclosed (EST)', 'Date', 'Traded Date', 'Filed Date']
for col in date_columns:
    if col in insider_df.columns:
        insider_df[col] = pd.to_datetime(insider_df[col], errors='coerce').dt.strftime('%Y-%m-%d')
    if col in congress_df.columns:
        congress_df[col] = pd.to_datetime(congress_df[col], errors='coerce').dt.strftime('%Y-%m-%d')

# Rename columns for consistency
congress_df.rename(columns={'Politician Name': 'Name', 
                            'Politician Position': 'Title', 
                            'Filed Date': 'Disclosed (EST)'}, inplace=True)

# Extract and convert transaction amount to numeric
if 'Transaction Amount' in congress_df.columns:
    congress_df['Transaction Amount'] = congress_df['Transaction Amount'].apply(
        lambda x: int(re.search(r'\$(\d[\d,]*)$', x).group(1).replace(',', '')) 
        if isinstance(x, str) and re.search(r'\$(\d[\d,]*)$', x) else None
    )

# Fetch open prices efficiently
if 'Date' in insider_df.columns:
    traded_dates_list = insider_df['Date'].tolist()
    open_prices = get_stock_open_prices(ticker, traded_dates_list)
    insider_df['Open Price'] = open_prices

# Ensure proper renaming after open price retrieval
insider_df.rename(columns={'Purchase/Sale': 'Transaction Type', 
                           'Politician Position': 'Title', 
                           'Date': 'Traded Date'}, inplace=True)

# Handle missing 'Shares' column gracefully
if 'Shares' in insider_df.columns:
    insider_df['Shares'] = pd.to_numeric(insider_df['Shares'], errors='coerce')
    insider_df['Transaction Amount'] = insider_df['Shares'] * insider_df['Open Price']
else:
    insider_df['Transaction Amount'] = None  # Default to None if Shares column is missing

# Merge DataFrames
merged_df = pd.concat([congress_df, insider_df], ignore_index=True)

# Drop unnecessary columns if they exist
merged_df.drop(columns=['Stock', 'Description', 'Shares', 'Open Price'], errors='ignore', inplace=True)

# Sort for easier grouping
merged_df_sorted = merged_df.sort_values(by=['Name', 'Title', 'Traded Date', 'Transaction Type'])

# Initialize list to store combined rows
combined_rows = []
current_group = None
total_amount = 0

# Iterate and combine rows based on Name, Title, Traded Date, and Transaction Type
for _, row in merged_df_sorted.iterrows():
    if current_group and (current_group == (row['Name'], row['Title'], row['Traded Date'], row['Transaction Type'])):
        total_amount += row['Transaction Amount']  # Sum the transaction amount
        last_disclosed = row['Disclosed (EST)']  # Update last disclosed date
    else:
        # Save the previous group and reset for the new group
        if current_group:
            combined_rows.append({
                'Name': current_group[0],
                'Title': current_group[1],
                'Traded Date': current_group[2],
                'Transaction Type': current_group[3],
                'Transaction Amount': total_amount,
                'Disclosed (EST)': last_disclosed
            })

        # Start a new group
        current_group = (row['Name'], row['Title'], row['Traded Date'], row['Transaction Type'])
        total_amount = row['Transaction Amount']
        last_disclosed = row['Disclosed (EST)']

# Append the last group after the loop ends
if current_group:
    combined_rows.append({
        'Name': current_group[0],
        'Title': current_group[1],
        'Traded Date': current_group[2],
        'Transaction Type': current_group[3],
        'Transaction Amount': total_amount,
        'Disclosed (EST)': last_disclosed
    })

# Create DataFrame from combined rows
insider_trades_df = pd.DataFrame(combined_rows)

# Ensure 'Traded Date' is datetime
insider_trades_df['Traded Date'] = pd.to_datetime(insider_trades_df['Traded Date'])

# Sort & Reset Index
insider_trades_df = insider_trades_df.sort_values(by='Traded Date').reset_index(drop=True)

import requests
import pandas as pd
from datetime import datetime, timedelta

# Load insider trading and congress trading datasets
insider_df = pd.read_csv(f"test_data/{ticker}/{ticker}_Insider_Trading.csv")
insider_df['Date'] = pd.to_datetime(insider_df['Date'], format="%b %d, %Y").dt.strftime("%Y-%m-%d")
congress_df = pd.read_csv(f"test_data/{ticker}/{ticker}_Congress_Trades.csv")

# Convert date columns to standardized YYYY-MM-DD format
date_columns = ['Disclosed (EST)', 'Date', 'Traded Date', 'Filed Date']
for col in date_columns:
    if col in insider_df.columns:
        insider_df[col] = pd.to_datetime(insider_df[col], errors='coerce').dt.strftime('%Y-%m-%d')
    if col in congress_df.columns:
        congress_df[col] = pd.to_datetime(congress_df[col], errors='coerce').dt.strftime('%Y-%m-%d')

# Rename columns for consistency
congress_df.rename(columns={
    'Politician Name': 'Name', 
    'Politician Position': 'Title', 
    'Filed Date': 'Disclosed (EST)'
}, inplace=True)

# Extract and convert transaction amount to numeric
congress_df['Transaction Amount'] = congress_df['Transaction Amount'].apply(
    lambda x: int(re.search(r'\$(\d[\d,]*)$', x).group(1).replace(',', '')) if isinstance(x, str) and re.search(r'\$(\d[\d,]*)$', x) else None
)

# ---- **Fetch Open Prices Efficiently** ----
# Get unique traded dates
traded_dates_list = insider_df['Date'].dropna().unique().tolist()

# Fetch open prices for all dates at once
open_prices = get_stock_open_prices(ticker, traded_dates_list)

# Map open prices back to the dataframe
open_price_map = dict(zip(traded_dates_list, open_prices))
insider_df['Open Price'] = insider_df['Date'].map(open_price_map)

# Rename columns for consistency
insider_df.rename(columns={'Purchase/Sale': 'Transaction Type', 'Date': 'Traded Date'}, inplace=True)

# Convert Shares to numeric and calculate Transaction Amount
insider_df['Shares'] = pd.to_numeric(insider_df['Shares'], errors='coerce').fillna(0)
insider_df['Open Price'] = pd.to_numeric(insider_df['Open Price'], errors='coerce').fillna(0)
insider_df['Open Price'] = insider_df['Open Price'].round(1)
insider_df['Transaction Amount'] = insider_df['Shares'] * insider_df['Open Price']

# Drop unnecessary columns
insider_df.drop(columns=['Stock', 'Description', 'Shares'], errors='ignore', inplace=True)

# ---- **Merge Insider & Congress DataFrames** ----
merged_df = pd.concat([congress_df, insider_df], ignore_index=True)

# Sort the merged DataFrame for easier grouping
merged_df_sorted = merged_df.sort_values(by=['Name', 'Title', 'Traded Date', 'Transaction Type'])

# ---- **Combine Trades from Same Person on Same Date** ----
combined_rows = []
current_group = None
total_amount = 0

# Iterate and combine rows based on Name, Title, Traded Date, and Transaction Type
for _, row in merged_df_sorted.iterrows():
    if current_group and (current_group == (row['Name'], row['Title'], row['Traded Date'], row['Transaction Type'])):
        total_amount += row['Transaction Amount']  # Sum the transaction amount
        last_disclosed = row['Disclosed (EST)']  # Update last disclosed date
    else:
        # Save the previous group and reset for the new group
        if current_group:
            combined_rows.append({
                'Name': current_group[0],
                'Title': current_group[1],
                'Traded Date': current_group[2],
                'Transaction Type': current_group[3],
                'Transaction Amount': total_amount,
                'Disclosed (EST)': last_disclosed
            })

        # Start a new group
        current_group = (row['Name'], row['Title'], row['Traded Date'], row['Transaction Type'])
        total_amount = row['Transaction Amount']
        last_disclosed = row['Disclosed (EST)']

# Append the last group after the loop ends
if current_group:
    combined_rows.append({
        'Name': current_group[0],
        'Title': current_group[1],
        'Traded Date': current_group[2],
        'Transaction Type': current_group[3],
        'Transaction Amount': total_amount,
        'Disclosed (EST)': last_disclosed
    })

# ---- **Create Final Cleaned DataFrame** ----
insider_trades_df = pd.DataFrame(combined_rows)

# Ensure 'Traded Date' is datetime format and sort
insider_trades_df['Traded Date'] = pd.to_datetime(insider_trades_df['Traded Date'])
insider_trades_df = insider_trades_df.sort_values(by='Traded Date').reset_index(drop=True)

static_df = insider_trades_df
# Define the cutoff as the last 30 days from today
if not sentiment_df.empty and 'general_sentiment_score' in sentiment_df.columns:
    latest_sentiment_score = sentiment_df['general_sentiment_score'].iloc[0]
    used_sentiment = True
else:
    latest_sentiment_score = 0  # or any fallback value
    used_sentiment = False

latest_zacks_score = zacks_rank

recent_cutoff = datetime.now() - timedelta(days=30)

# Convert 'Traded Date' to datetime format if not already
static_df["Traded Date"] = pd.to_datetime(static_df["Traded Date"])

# Assign latest scores only to recent transactions
static_df["Zacks Score"] = static_df["Traded Date"].apply(
    lambda x: latest_zacks_score if x >= recent_cutoff else None
)

static_df["Sentiment Score"] = static_df["Traded Date"].apply(
    lambda x: latest_sentiment_score if x >= recent_cutoff else None
)
static_df.to_csv(f"test_data\{ticker}\{ticker}_Static_Data.csv", index=False)
        
import requests
def extract_article_text(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract all paragraphs
            paragraphs = soup.find_all('p')
            article_text = ' '.join([p.get_text(strip=True) for p in paragraphs])

            if not article_text.strip():
                return "Could not extract text. Might be paywalled."
            
            return article_text
        else:
            return f"Failed with status code {response.status_code}"

    except requests.exceptions.RequestException as e:
        return f"Request failed: {e}"

import pandas as pd
def fetch_polygon_news(ticker, api_key='LTikapZvdZjraWfVP2r_QgAvTX_oZSZw'):
    """
    Fetches the latest news articles for a given stock ticker using Polygon.io's News API and extracts the article text,
    filtering out articles from The Motley Fool (i.e. URLs containing "fool.com").
    """
    base_url = 'https://api.polygon.io/v2/reference/news'
    params = {
        'ticker': ticker,
        'limit': 100,
        'order': 'descending',
        'sort': 'published_utc',
        'apiKey': api_key
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        articles = data.get('results', [])
        
        # Extract relevant information, filtering out articles from fool.com
        news_data = []
        for article in articles:
            url = article.get('article_url', '')
            # Skip articles with URLs that contain "fool.com"
            if url and "fool.com" in url.lower():
                continue
            
            title = article.get('title', 'No Title')
            published = article.get('published_utc', 'Unknown Date')
            # Here extract_article_text is assumed to be defined elsewhere.
            text = extract_article_text(url) if url else None
            
            news_data.append({
                'Title': title,
                'Published': published,
                'URL': url,
                'Text': text
            })
        
        return pd.DataFrame(news_data)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching news: {e}")
        return pd.DataFrame()
    
import pandas as pd
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer

# Load FinBERT for financial sentiment analysis
MODEL_NAME = "ProsusAI/finbert"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
sentiment_pipeline = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)



def drcr_sentiment_analysis(article_text):
    """
    Apply Dual Reverse Chain Reasoning (DRCR) for implicit sentiment analysis.
    Only the first 500 words of the article text are used.
    Returns a dictionary with:
      - 'dummy': the sentiment label ("positive", "negative", or "neutral")
      - 'score': the corresponding confidence score
    """
    # Truncate the text to the first 500 words
    words = article_text.split()[:500]
    truncated_text = ' '.join(words)
    
    # Use the sentiment pipeline with truncation (max 512 tokens)
    positive_reasoning = sentiment_pipeline(
        f"Considering a positive market sentiment: {truncated_text}",
        truncation=True,
        max_length=512
    )[0]
    negative_reasoning = sentiment_pipeline(
        f"Considering a negative market sentiment: {truncated_text}",
        truncation=True,
        max_length=512
    )[0]
    
    # Retrieve labels in lowercase for consistency
    pos_label = positive_reasoning['label'].lower()
    neg_label = negative_reasoning['label'].lower()
    
    # Calculate adjusted confidence scores
    pos_score = positive_reasoning['score'] if pos_label == 'positive' else 1 - positive_reasoning['score']
    neg_score = negative_reasoning['score'] if neg_label == 'negative' else 1 - negative_reasoning['score']
    
    # Determine final sentiment based on contrastive reasoning
    if pos_score > neg_score:
        return {"dummy": "positive", "score": pos_score}
    elif neg_score > pos_score:
        return {"dummy": "negative", "score": neg_score}
    else:
        return {"dummy": "neutral", "score": (pos_score + neg_score) / 2}
    


def assign_news_score(static_df, news_df, tolerance='7D'):
    """
    Assigns a news sentiment score to each row in static_df based on the news article
    whose 'Published' date is closest to the static_df's 'Traded Date'. If no news article
    is found within the tolerance, a score of 0 is assigned.
    
    Parameters:
        static_df (pd.DataFrame): DataFrame with a 'Traded Date' column.
        news_df (pd.DataFrame): DataFrame with 'Published' (date) and 'score' (sentiment score) columns.
        tolerance (str): Maximum difference between 'Traded Date' and 'Published' date (default '7D').
        
    Returns:
        pd.DataFrame: static_df with a new column 'News Score' added.
    """
    # Convert date columns to datetime
    static_df['Traded Date'] = pd.to_datetime(static_df['Traded Date'], errors='coerce')
    news_df['Published'] = pd.to_datetime(news_df['Published'], errors='coerce')
    
    # Sort both DataFrames by their respective date columns
    static_df_sorted = static_df.sort_values('Traded Date').reset_index(drop=True)
    news_df_sorted = news_df.sort_values('Published').reset_index(drop=True)
    
    # Perform an asof merge to match each traded date with the nearest published date within tolerance
    merged = pd.merge_asof(static_df_sorted, 
                           news_df_sorted[['Published', 'score']], 
                           left_on='Traded Date', 
                           right_on='Published', 
                           direction='nearest', 
                           tolerance=pd.Timedelta(tolerance))
    
    # If no news article was found, 'score' will be NaN. Replace NaN with 0.
    merged['score'] = merged['score'].fillna(0)
    
    # Add the 'News Score' column to the static_df
    static_df_sorted['News Score'] = merged['score']
    
    return static_df_sorted

def drcr_sentiment(ticker, api_key = 'LTikapZvdZjraWfVP2r_QgAvTX_oZSZw'):
    df = fetch_polygon_news(ticker, api_key)
    df['Published'] = pd.to_datetime(df['Published'], errors='coerce').dt.strftime('%Y-%m-%d')
    df['result'] = df['Text'].apply(drcr_sentiment_analysis)
    # Expand the dictionary into two new columns: 'dummy' and 'score'
    df[['dummy', 'score']] = df['result'].apply(pd.Series)
    df = df.drop(columns=['result'])
    return df

static_df = insider_trades_df
# Define the cutoff as the last 30 days from today
if not sentiment_df.empty and 'general_sentiment_score' in sentiment_df.columns:
    latest_sentiment_score = sentiment_df['general_sentiment_score'].iloc[0]
    used_sentiment = True
else:
    latest_sentiment_score = 0  # or any fallback value
    used_sentiment = False

latest_zacks_score = zacks_rank

recent_cutoff = datetime.now() - timedelta(days=30)

# Convert 'Traded Date' to datetime format if not already
static_df["Traded Date"] = pd.to_datetime(static_df["Traded Date"])

# Assign latest scores only to recent transactions
static_df["Zacks Score"] = static_df["Traded Date"].apply(
    lambda x: latest_zacks_score if x >= recent_cutoff else None
)

static_df["Sentiment Score"] = static_df["Traded Date"].apply(
    lambda x: latest_sentiment_score if x >= recent_cutoff else None
)
static_df.to_csv(f"test_data\{ticker}\{ticker}_Static_Data.csv", index=False)

from sklearn.preprocessing import LabelEncoder
import pandas as pd
from datetime import datetime

# Drop 'Zacks Score' and 'Sentiment Score' if they exist
static_df = static_df.drop(columns=['Zacks Score', 'Sentiment Score'], errors='ignore')

# One-hot encoding for 'Transaction Type' and 'Name'
static_df = pd.get_dummies(static_df, columns=['Transaction Type'], dtype=int)
static_df = pd.get_dummies(static_df, columns=['Name'], dtype=int)

# Encode 'Title' using Label Encoding
title_encoder = LabelEncoder()
if "Title" in static_df.columns:
    static_df['Title'] = title_encoder.fit_transform(static_df['Title'])
    static_df['Title'] = static_df['Title'].astype(int)

# Convert date columns to datetime format (only if they exist)
if "Traded Date" in static_df.columns:
    static_df["Traded Date"] = pd.to_datetime(static_df["Traded Date"], errors="coerce")
if "Disclosed (EST)" in static_df.columns:
    static_df["Disclosed (EST)"] = pd.to_datetime(static_df["Disclosed (EST)"], errors="coerce")

# Calculate disclosure delay (only if both columns exist)
if "Traded Date" in static_df.columns and "Disclosed (EST)" in static_df.columns:
    static_df["Disclosure Delay"] = (static_df["Disclosed (EST)"] - static_df["Traded Date"]).dt.days

# Handle missing 'Quarter_score' column
if "Quarter_score" in static_df.columns and static_df["Quarter_score"].notna().any():
    static_df["Quarter_score"] = static_df["Quarter_score"].astype(str).str.extract(r'(\d+)/\d+')
    static_df["Quarter_score"] = pd.to_numeric(static_df["Quarter_score"], errors='coerce').astype('Int64')
else:
    # If 'Quarter_score' is missing or empty, filter data to include only the current and last year
    if "Traded Date" in static_df.columns:
        current_year = datetime.now().year
        static_df = static_df[static_df["Traded Date"].dt.year >= current_year - 1]
        print("'Quarter_score' is missing or empty. Using only data from the current and last year.")
    else:
        print("'Traded Date' is missing. Skipping year-based filtering.")

# Drop date columns only after all processing is done
static_df = static_df.drop(columns=["Disclosed (EST)"], errors="ignore")

# Convert boolean columns to integers
bool_cols = static_df.select_dtypes(include=bool).columns
static_df[bool_cols] = static_df[bool_cols].astype(int)
static_df = static_df.reset_index(drop=True)
print("Data processing completed successfully.")

static_covariates = pd.DataFrame(static_df.mean()).T

news_df = drcr_sentiment(ticker, api_key = 'LTikapZvdZjraWfVP2r_QgAvTX_oZSZw')

static_with_news = assign_news_score(static_df, news_df, tolerance='7D')
if used_sentiment:
    static_with_news = static_with_news[static_with_news['News Score'] != 0].reset_index(drop=True)

technical_df = technical_polygon(symbol = ticker, interval = interval, interval_range = interval_range, days = days)
technical_df.to_csv(f"test_data\{ticker}\{ticker}_Technical_Data.csv", index=False)

live_df = technical_df
live_df.reset_index(inplace=True)
live_df.to_csv(f"test_data\{ticker}\{ticker}_Live_Data.csv", index=False)

live_df = pd.read_csv(f"test_data\{ticker}\{ticker}_Live_Data.csv")
stock_live_df = pd.read_csv(f"test_data\{ticker}\{ticker}_Live_Data.csv")

live_df = live_df.loc[:, : 'Stochastic']
stock_live_df = stock_live_df.loc[:, : 'Stochastic']

live_df['y'] = live_df['close'].shift(-10)

static_covariates = pd.DataFrame(static_with_news.mean()).T

import pandas as pd
from darts import TimeSeries

def getXY(df1, forecasting_horizon):
    """
    Prepares data for multi-step forecasting.
    
    Parameters:
      df1: pd.DataFrame
          DataFrame that must contain at least the columns 'timestamp' and 'close'
      n: int
          Window size (number of past data points to use)
      forecasting_horizon: int
          Number of steps ahead to predict (target is close price shifted by this many steps)
    
    Returns:
      X_series: TimeSeries
          TimeSeries of past covariates (all columns except 'timestamp' and 'y')
      y_series: TimeSeries
          TimeSeries of target variable 'y' (close price forecasting_horizon ahead)
      xdf: pd.DataFrame
          DataFrame version of the covariate data
      ydf: pd.DataFrame
          DataFrame of the target values and timestamps
    """
    # Copy the data to avoid modifying the original DataFrame
    df = df1.copy()
    
    # Convert timestamps and set as index
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df.set_index('timestamp', inplace=True)
    
    # Resample to ensure regular 5-minute intervals and fill missing data
    df = df.resample('5T').asfreq()
    df.fillna(method='ffill', inplace=True)
    
    # Reset index to bring timestamp back as a column
    df = df.reset_index()
    
    # Create the target column 'y' as the close price forecasting_horizon steps ahead
    df['y'] = df['close'].shift(-forecasting_horizon)
    
    # Remove the last forecasting_horizon rows that have NaN as target
    df = df.iloc[:-forecasting_horizon].copy()
    
    # Create DataFrames: 
    # xdf contains all features, and ydf holds only the target 'y' with its timestamp.
    xdf = df.copy()
    ydf = df[['timestamp', 'y']].copy()
    
    # Build TimeSeries objects:
    # y_series uses the 'y' column as the target
    y_series = TimeSeries.from_dataframe(ydf,
                                         time_col='timestamp',
                                         value_cols='y',
                                         freq='5min',
                                         fill_missing_dates=True)
    # X_series uses all columns except 'timestamp' and 'y' (i.e. the past covariates)
    cov_cols = [col for col in xdf.columns if col not in ['timestamp', 'y']]
    X_series = TimeSeries.from_dataframe(xdf,
                                         time_col='timestamp',
                                         value_cols=cov_cols,
                                         freq='5min',
                                         fill_missing_dates=True)
    
    return X_series, y_series, xdf, ydf

# Prepare the data
X_series, y_series, xdf, ydf = getXY(live_df, forecasting_horizon)

xdf['y'] = ydf['y'].values
series = TimeSeries.from_dataframe(xdf,
                                   value_cols = 'y',
                                   time_col = 'timestamp',
                                   fill_missing_dates=True,
                                    freq="5min",
                                   static_covariates = static_covariates)
scaler1 = Scaler()
scaler2 = Scaler()
y_transformed = scaler1.fit_transform(y_series)
past_covariates_transformed = scaler2.fit_transform(series)
y_transformed_df = y_transformed.pd_dataframe()
past_covariates_transformed_df = past_covariates_transformed.pd_dataframe()
y_transformed_df = y_transformed_df.fillna(method='ffill').fillna(method='bfill')
past_covariates_transformed_df = past_covariates_transformed_df.fillna(method='ffill').fillna(method='bfill')

from darts import TimeSeries

y_transformed_clean = TimeSeries.from_dataframe(y_transformed_df)
past_covariates_transformed_clean = TimeSeries.from_dataframe(past_covariates_transformed_df)
past_covariates_transformed_df = past_covariates_transformed_df.iloc[-17157:]
past_covariates_transformed_clean = TimeSeries.from_dataframe(past_covariates_transformed_df)
y_transformed_clean = y_transformed_clean[-7506:]
y_transformed_clean = y_transformed_clean.astype('float32')
past_covariates_transformed_clean = past_covariates_transformed_clean.astype('float32')

import pandas as pd
from darts.models import TFTModel
from darts.dataprocessing.transformers import Scaler

def encode_hour(idx):
    return idx.hour / 24

# Manually define add_encoders
add_encoders = {
    'cyclic': {'future': ['hour', 'day', 'dayofweek', 'week', 'month']},
    'datetime_attribute': {'future': ['hour', 'day', 'dayofweek', 'week', 'month']},
    'position': {'past': ['relative'], 'future': ['relative']},
    'custom': {'past': [encode_hour], 'future': [encode_hour]},
    'transformer': Scaler(),
    'tz': 'CET'
}

# Load best parameters
best_params_df = pd.read_csv(f'NVDA/NVDA_best_params.csv')
best_params = best_params_df.iloc[0]  # Select first row

# Convert parameters to correct types
best_params_dict = {
    'output_chunk_length': int(best_params['output_chunk_length']),
    'num_attention_heads': int(best_params['num_attention_heads']),
    'n_epochs': int(best_params['n_epochs']),
    'lstm_layers': int(best_params['lstm_layers']),
    'input_chunk_length': int(best_params['input_chunk_length']),
    'hidden_size': int(best_params['hidden_size']),
    'dropout': float(best_params['dropout']),
    'batch_size': int(best_params['batch_size']),
    'use_static_covariates': bool(best_params['use_static_covariates']),
    'add_encoders': add_encoders,
    'pl_trainer_kwargs': {'accelerator': 'cpu'}  # Adjust as needed
}

# Build and train the model
model = TFTModel(**best_params_dict)

model.fit(
    y_transformed_clean,
    past_covariates=past_covariates_transformed_clean
)

print("Model training completed successfully.")

def make_markov_chain_transition_matrix(df, close_column_name="close"):
    transition_matrix = np.zeros((2, 2))
    df["Trend"] = np.where(df[close_column_name].diff() > 0, 1, 0)
    for i in range(1, len(df)):
        prev_state = df["Trend"].iloc[i - 1]
        curr_state = df["Trend"].iloc[i]
        transition_matrix[prev_state, curr_state] += 1
    transition_matrix = transition_matrix / transition_matrix.sum(axis=1, keepdims=True)
    transition_matrix = np.nan_to_num(transition_matrix, nan=0.5)  # Fix NaN cases
    return transition_matrix
def predict_next_trend(current_state, transition_matrix):
    return np.random.choice([0, 1], p=transition_matrix[current_state])

live_df_copy = live_df.copy()
transition_matrix = make_markov_chain_transition_matrix(live_df_copy, close_column_name="close")

trend = predict_next_trend(live_df_copy["Trend"].iloc[-1], transition_matrix)
print(f"Predicted Next Trend: {'Bullish' if trend == 1 else 'Bearish'}")

def calculate_adx_rsi(df, high_col="High", low_col="Low", close_col="Close", period=14):
    df = df.copy()
    df["TR"] = np.maximum(df[high_col] - df[low_col], 
                          np.maximum(abs(df[high_col] - df[close_col].shift(1)), 
                                     abs(df[low_col] - df[close_col].shift(1))))
    
    df["+DM"] = np.where((df[high_col] - df[high_col].shift(1)) > (df[low_col].shift(1) - df[low_col]),
                         np.maximum(df[high_col] - df[high_col].shift(1), 0), 0)
    df["-DM"] = np.where((df[low_col].shift(1) - df[low_col]) > (df[high_col] - df[high_col].shift(1)),
                         np.maximum(df[low_col].shift(1) - df[low_col], 0), 0)
    df["ATR"] = df["TR"].rolling(window=period).mean()
    df["+DM_Smooth"] = df["+DM"].rolling(window=period).mean()
    df["-DM_Smooth"] = df["-DM"].rolling(window=period).mean()
    df["+DI"] = (df["+DM_Smooth"] / df["ATR"]) * 100
    df["-DI"] = (df["-DM_Smooth"] / df["ATR"]) * 100
    df["DX"] = (abs(df["+DI"] - df["-DI"]) / (df["+DI"] + df["-DI"])) * 100
    df["ADX"] = df["DX"].rolling(window=period).mean()
    delta = df[close_col].diff(1)
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)

    avg_gain = pd.Series(gain).rolling(window=period, min_periods=1).mean()
    avg_loss = pd.Series(loss).rolling(window=period, min_periods=1).mean()

    rs = avg_gain / avg_loss
    df["RSI"] = 100 - (100 / (1 + rs))
    last_adx = df["ADX"].iloc[-1]
    last_rsi = df["RSI"].iloc[-1]
    trend_confirmed = last_adx > 25
    rsi_divergence = last_rsi > 70 or last_rsi < 30

    return trend_confirmed, rsi_divergence

trend_confirmed, rsi_divergence = calculate_adx_rsi(live_df_copy, high_col="high", low_col="low", close_col="close")

print(f"Trend Confirmed: {trend_confirmed}")
print(f"RSI Divergence Detected: {rsi_divergence}")


from datetime import datetime, timedelta
import pandas as pd
import requests

def fetch_polygon_data(ticker, timespan, first_pred=False, limit=500, intervel_time=15):
    """Fetch historical data from Polygon.io."""
    api_key = "6FScTtPXo3hC4lyzkRb29mNJOOmLYwYF"
    end_date = datetime.now()
    
    if first_pred:
        live_df = pd.read_csv(f"{ticker}/{ticker}_Live_Data.csv")
        live_df['timestamp'] = pd.to_datetime(live_df['timestamp'], errors='coerce')
        # Use the day before the first timestamp in live_df
        live_date = pd.to_datetime(live_df['timestamp'].iloc[0]) - pd.Timedelta(days=1)
        # Format the date as YYYY-MM-DD for Polygon API
        start_date = live_date.strftime("%Y-%m-%d")
    else:
        start_date = (end_date - timedelta(days=5)).strftime("%Y-%m-%d")
    
    formatted_end_date = end_date.strftime("%Y-%m-%d")
    
    url = (f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/{intervel_time}/{timespan}/"
           f"{start_date}/{formatted_end_date}?adjusted=true&sort=desc&limit={limit}&apiKey={api_key}")
    
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if "results" in data:
            df = pd.DataFrame(data["results"])
            df["timestamp"] = pd.to_datetime(df["t"], unit="ms")
            return df[["timestamp", "o", "h", "l", "c", "v"]].rename(
                columns={"o": "open", "h": "high", "l": "low", "c": "close", "v": "volume"})
    return pd.DataFrame()

def is_market_open():
    """Check if the market is currently open using Polygon's market status endpoint."""
    api_key = "6FScTtPXo3hC4lyzkRb29mNJOOmLYwYF"
    url = f"https://api.polygon.io/v1/marketstatus/now?apiKey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get("market", "closed") == "open"
    return False


import pandas as pd
from darts import TimeSeries
from darts.dataprocessing.transformers import Scaler

def buy_signal(n_df, min_df, n, static_covariates, forecasting_horizon, first_pred=False):
    '''
    Model parameters:
    output_chunk_length: 20
    num_attention_heads: 2
    n_epochs: 8
    lstm_layers: 1
    input_chunk_length: 100
    hidden_size: 24
    dropout: 0.2
    batch_size: 32
    use_static_covariates: True
    add_encoders: {'cyclic': {'future': ['hour', 'day', 'dayofweek', 'week', 'month']}, 
                   'datetime_attribute': {'future': ['hour', 'day', 'dayofweek', 'week', 'month']}, 
                   'position': {'past': ['relative'], 'future': ['relative']}, 
                   'custom': {'past': [<function encode_hour at 0x00000181ED22B040>], 
                              'future': [<function encode_hour at 0x00000181ED22B040>]}, 
                   'transformer': Scaler, 'tz': 'CET'}
    pl_trainer_kwargs: {'accelerator': 'cpu'}
    '''
    """
    Determines a buy signal based on technical indicators, a Markov Chain trend, and a TFT model forecast.
    
    Parameters:
        n_df (DataFrame): Higher timeframe DataFrame (e.g., 15min data) with at least a 'close' column.
        min_df (DataFrame): Minute-level DataFrame used for technical indicator calculations (ADX, RSI, etc.).
        n (int): Number of time steps used for shifting to create the target column.
        static_covariates (DataFrame): Static covariates for the TimeSeries.
        forecasting_horizon (int): Number of steps ahead to forecast.
        first_pred (bool): Flag for first prediction logic.
        
    Returns:
        bool: The resulting buy signal.
    """
    # Debug: print initial columns and first two rows of n_df
    # Apply technical indicators (assumed to be defined elsewhere)
    n_df = technical_indicators(n_df)
    n_df.reset_index(inplace=True)  # Ensure 'timestamp' is a column
    
    # Create target column 'y' by shifting the 'close' column up by n steps
    n_df['y'] = n_df['close'].shift(-n)
    n_df.dropna(inplace=True)  # Drop rows with NaN (from shifting)
    
    # Copy the processed DataFrame for later use if needed
    stock_live_df = n_df.copy()
    
    # Restrict n_df to columns up to 'Stochastic'
    n_df = n_df.loc[:, :'Stochastic']
    # If 'y' is missing due to the slice, re-add it from the copy
    if 'y' not in n_df.columns:
        n_df['y'] = stock_live_df['y']
        
    # Do the same for stock_live_df if needed
    stock_live_df = stock_live_df.loc[:, :'Stochastic']
    if 'y' not in stock_live_df.columns:
        stock_live_df['y'] = n_df['y']
    
    # Ensure the timestamp column is in datetime format and drop rows with issues
    stock_live_df['timestamp'] = pd.to_datetime(stock_live_df['timestamp'], errors='coerce')
    stock_live_df.dropna(inplace=True)
    
    # Create a Darts TimeSeries using the 'y' column as the target.
    series = TimeSeries.from_dataframe(
        stock_live_df,
        value_cols='y',
        time_col='timestamp',
        fill_missing_dates=True,
        freq="5T",  
        static_covariates=static_covariates
    )
    
    # Cast the series to float32 to ensure compatibility with the model
    series = series.astype("float32")
    
    # Normalize input data using a Scaler
    scaler2 = Scaler()
    past_covariates_transformed = scaler2.fit_transform(series)
    
    # --- Debug prints for past covariates ---
    past_covariates_df = past_covariates_transformed.pd_dataframe()
    current_end = past_covariates_transformed.end_time()
    
    # Print model specifications (assumes a global variable 'model')
    print("Model specifications:")
    print(model)

    
    # The model expects the past covariates to extend until 2025-03-11 14:30:00.
    required_end = pd.Timestamp("2025-03-11 14:30:00")
    freq = pd.Timedelta(minutes=5)
    if current_end < required_end:
        extra_steps = int(((required_end - current_end).total_seconds() / 300) + 1)
        print("Extending past covariates by", extra_steps, "steps")
        last_val = past_covariates_transformed.last_value()
        extra_times = pd.date_range(start=current_end + freq, periods=extra_steps, freq="5T")
        extra_series = TimeSeries.from_times_and_values(extra_times, [last_val]*extra_steps)
        past_covariates_transformed = past_covariates_transformed.concatenate(extra_series)
    
    # Ensure past_covariates_transformed is float32 after extension
    past_covariates_transformed = past_covariates_transformed.astype("float32")
    
    print("Past covariates end_time after extension:", past_covariates_transformed.end_time())
    
    # --- Forecast using the trained model ---
    # IMPORTANT: Pass both the target series and the past covariates.
    forecast = model.predict(n=forecasting_horizon,
                             series=series, 
                             past_covariates=past_covariates_transformed)
    
    forecast_values = scaler2.inverse_transform(forecast).values().flatten()
    forecast_df = pd.DataFrame({"forecast_values": forecast_values})
    
    # Calculate ADX and RSI from minute-level data (assumed defined elsewhere)
    trend_confirmed, rsi_divergence = calculate_adx_rsi(min_df, high_col="high", low_col="low", close_col="close")
    
    # Predict next trend using Markov Chain (assumed defined elsewhere)
    transition_matrix = make_markov_chain_transition_matrix(n_df, close_column_name="close")
    trend = predict_next_trend(n_df["Trend"].iloc[-1], transition_matrix)
    
    # Compute conditions based on the first close price and forecasted mean

    # Calculate % difference between close[1] and close[0]
    close_diff = abs(n_df['close'].iloc[1] - n_df['close'].iloc[0]) / n_df['close'].iloc[0]

    # Calculate % difference between forecast[1] and forecast[0]
    forecast_diff = abs(forecast_df['forecast_values'].iloc[1] - forecast_df['forecast_values'].iloc[0]) / forecast_df['forecast_values'].iloc[0]

    # Compare the differences
    first_a = close_diff < forecast_diff
    
    a = forecast_df['forecast_values'].iloc[3] < forecast_df['forecast_values'].mean()
    
    print("First condition, prediction based):", first_a)
    print("RSI Divergence:", rsi_divergence)
    
    if rsi_divergence and first_a:
        return True
    else:
        return False

#=============================================================================================================

# Assumes that fetch_polygon_data, ticker, interval_range, forecasting_horizon,
# static_covariates, and df_simulation are defined elsewhere.

pos = 0
print(f'Connecting to PORT {port}')
connect(port=port , client_id=100)

while True:
    if is_market_open() or this_is_a_test:
        print("Market is open. Fetching new data...")
        df_15min = fetch_polygon_data(ticker, "minute", limit=1000, intervel_time=f'{interval_range}')
        df_1min = fetch_polygon_data(ticker, "minute", limit=1000, intervel_time=f'{round(interval_range/5)}')
        df_15min = df_15min.iloc[::-1].reset_index(drop=True)
        df_1min = df_1min.iloc[::-1].reset_index(drop=True)
        
        signal = buy_signal(
            n_df=df_15min,
            min_df=df_1min,
            static_covariates=static_covariates,
            first_pred=first_pred,
            n=forecasting_horizon,
            forecasting_horizon=forecasting_horizon
        )
        print(signal)
        if signal:
            buy(ticker, quantity=2)
            print('buy')
            pos = 1
        elif pos == 1 and signal == False:
            close_buy(ticker, quantity=2)
            print('close_buy')

        
        results_df = pd.concat([
            results_df,
            pd.DataFrame({
                "timestamp": [df_15min.iloc[0]["timestamp"]],
                "Buy_Signal": [signal],
                "close": df_15min.iloc[0]['close']
            })
        ], ignore_index=True)
        
        if this_is_a_test:
            this_is_a_test = False
            break
        first_pred = False
        print("Updated data and signals.")
        time.sleep(time_slept)
    else:
        print("Market is closed. Waiting...")
    
# Save results at the end of the day
results_df.to_csv(f"{ticker}_buy_signals.csv", index=False)
results_df = results_df.drop(columns=['Close', 'Timestamp'])
print("Market closed. Results saved.")
disconnect()