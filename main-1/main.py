import json
import requests        
import time
import pandas as pd
import os
import threading
import datetime
import matplotlib.pyplot as plt

from fpdf import FPDF

from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order
from ibapi.execution import ExecutionFilter

import yfinance as yf

#Best is the chosen ticker, but you can change it to any other ticker you want by chnging the value below:
if 'best' not in globals() or best is None:
    ticker = 'BWMX'
else:
    ticker = best['Symbol']  

TICKER = ticker
interval = "minute"
long_interval_range = 30
interval_range = 5
days = 100
long_days = 360
use_static_cov = True
time_slept = 60 * 2 
this_is_a_test = False
first_pred = True
USE_STATIC_COV = False
forecasting_horizon = 12

import os
import re
import time
from datetime import datetime, timedelta
from fpdf import FPDF
from datetime import date
import json

import pandas as pd
import numpy as np

import requests
from bs4 import BeautifulSoup

import threading
import time
import requests
import pandas as pd

from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order

from darts import TimeSeries
import darts
from darts.models import TFTModel
from darts.models.forecasting.tft_model import TFTModel  
from darts.dataprocessing.transformers import Scaler

from sklearn.preprocessing import LabelEncoder
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification

from utils.news import scrape_insider_data, scrape_congress_trading_data, sentiment, get_zacks_rank
from utils.fundamental import fundamental
from utils.technical import get_stock_open_prices, technical_polygon, technical_indicators

def get_api_key(key_name: str, file_path: str = "main-1/utils/api_keys.json") -> str:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"API key file '{file_path}' not found.")

    with open(file_path, "r") as f:
        api_keys = json.load(f)

    if key_name not in api_keys:
        raise KeyError(f"API key for '{key_name}' not found in '{file_path}'.")

    return api_keys[key_name]

def get_live_stock_data(ticker: str, rows: int = 30) -> pd.DataFrame:
    api_key = get_api_key("twelvedata")
    url = f"https://api.twelvedata.com/time_series?symbol={ticker}&interval=1min&apikey={api_key}&outputsize={rows}"
    response = requests.get(url).json()

    if "values" not in response:
        raise Exception("Error fetching live data: " + str(response))

    data = response["values"]
    df = pd.DataFrame([{
        "timestamp": pd.to_datetime(item["datetime"]),
        "open": float(item["open"]),
        "high": float(item["high"]),
        "low": float(item["low"]),
        "close": float(item["close"]),
        "volume": float(item["volume"]),
    } for item in data])

    df = df.sort_values("timestamp").reset_index(drop=True)
    return df

def get_zacks_rank(symbol):
    try:
        url = f"https://www.zacks.com/stock/quote/{symbol}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status() 

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the Zacks Rank
        rank_tag = soup.find('p', class_='rank_view')
        
        if rank_tag:
            rank_text = rank_tag.text.strip()
            return float(rank_text[0])  
        else:
            return float('nan')  # Return NaN if the rank is not found
    
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching data for {symbol}: {e}")
        return float('nan')

def is_nyse_open():
    url = "https://finance.yahoo.com/quote/%5EGSPC/"
    headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception("Failed to fetch market status")
    
    soup = BeautifulSoup(response.text, "html.parser")
    market_status = soup.select_one('#nimbus-app > section > section > section > article > section.container.yf-k4z9w > div.bottom.yf-k4z9w > div.price.yf-k4z9w > section > div > section > div.marketTime.yf-6mbnpm > span > span')
    if market_status:
        return "open" in market_status.text.lower()
    
    raise Exception("Could not determine market status")

def analyze_financial_news(texts):
    finbert = pipeline("text-classification", model="ProsusAI/finbert", device=-1)
    
    MAX_TOKENS = 512
    truncated_texts = [text[:MAX_TOKENS] for text in texts]

    predictions = finbert(truncated_texts)
    return predictions

def extract_article_text(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        article_body = soup.find('div', {'class': 'body yf-tsvcyu'})
        paragraphs = article_body.find_all('p') if article_body else []
        article_text = ' '.join([p.get_text(strip=True) for p in paragraphs])

        return article_text
    else:
        print("Failed to retrieve the content. Status code:", response.status_code)
        return None

def get_latest_news_df(stock_symbol):
    url = f"https://finance.yahoo.com/quote/{stock_symbol}/news"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        news_items = soup.find_all('a', class_='subtle-link fin-size-small titles noUnderline yf-1xqzjha')
        
        news = []
        for item in news_items:
            headline = item.get_text(strip=True)
            link = item['href']
            full_link = link
            news.append({'Headline': headline, 'URL': full_link})

        yf_links_df = pd.DataFrame(news)

        return yf_links_df
    else:
        print("Failed to retrieve the news. Status code:", response.status_code)
        return None

def get_symbols_from_excel():
    file_path = "Top_80_S&P_Companies.xlsx"
    try:
        df = pd.read_excel(file_path)
        
        symbols = df['Symbol'].tolist()
        
        return symbols
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def sentiment(symbols):
    symbols_sentiment_results = []

    for symbol in symbols:
        news_df = get_latest_news_df(symbol)

        if news_df is not None and not news_df.empty and 'Headline' in news_df.columns:
            symbol_sentiment_results = analyze_financial_news(list(news_df['Headline']))

            general_sentiment_score = 0
            for result in symbol_sentiment_results:
                if result['score'] >= 0.65:
                    if result['label'] == 'positive':
                        general_sentiment_score += 1
                    elif result['label'] == 'negative':
                        general_sentiment_score -= 1

            symbols_sentiment_results.append({
                "symbol": symbol,
                "general_sentiment_score": general_sentiment_score
            })
        else:
            symbols_sentiment_results.append({
                "symbol": symbol,
                "general_sentiment_score": 0
            })

    df = pd.DataFrame(symbols_sentiment_results)
    current_date = datetime.now().strftime('%d-%m-%Y')
    file_path = f'sentiment_report-{current_date}.xlsx'
    df.to_excel(file_path, index=False)
    print(f"Sentiment Report saved as {file_path}")
    return df

def scrape_congress_trading_data(symbol: str) -> pd.DataFrame:
    url = f"https://www.quiverquant.com/congresstrading/stock/{symbol}?"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve data for {symbol}. Status code: {response.status_code}")
        return pd.DataFrame()
    soup = BeautifulSoup(response.content, 'html.parser')
    table_body = soup.find('tbody')
    if not table_body:
        print(f"No data found for {symbol}.")
        return pd.DataFrame()
    rows = table_body.find_all('tr')
    data = []
    for row in rows:
        cols = row.find_all('td')
        if len(cols) < 6:
            continue
        stock_info = cols[0].find_all('span')
        stock = stock_info[0].get_text(strip=True) if stock_info else ""
        
        transaction_info = cols[1].find_all('span')
        transaction_type = transaction_info[0].get_text(strip=True) if transaction_info else ""
        transaction_amount = transaction_info[1].get_text(strip=True) if len(transaction_info) > 1 else ""
        
        politician_info = cols[2].find_all('span')
        politician_name = politician_info[0].get_text(strip=True) if politician_info else ""
        politician_position = politician_info[1].get_text(strip=True) if len(politician_info) > 1 else ""
        
        filed_date = cols[3].get_text(strip=True)
        traded_date = cols[4].get_text(strip=True)
        description = cols[5].get_text(strip=True)

        data.append([stock, transaction_type, transaction_amount, politician_name, politician_position, filed_date, traded_date, description])

    df = pd.DataFrame(data, columns=['Stock', 'Transaction Type', 'Transaction Amount', 'Politician Name', 'Politician Position', 'Filed Date', 'Traded Date', 'Description'])
    
    return df

def scrape_insider_data(symbol: str) -> pd.DataFrame:
    url = f"https://www.quiverquant.com/insiders/{symbol}?"
    
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"Failed to retrieve data for {symbol}. Status code: {response.status_code}")
        return pd.DataFrame()
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    table_body = soup.find('tbody')
    
    if not table_body:
        print(f"No data found for {symbol}.")
        return pd.DataFrame()

    rows = table_body.find_all('tr')
    
    data = []

    for row in rows:
        cols = row.find_all('td')
        if len(cols) < 5:
            continue

        name_title_div = cols[0].find('div', class_='flex-column')
        name = name_title_div.find('span').get_text(strip=True)
        title = name_title_div.find('span', class_='name-title').get_text(strip=True) if name_title_div.find('span', class_='name-title') else ""

        purchase_sale = cols[1].get_text(strip=True)
        shares = cols[2].get_text(strip=True)
        date = cols[3].get_text(strip=True)
        disclosed_est = cols[4].get_text(strip=True)

        data.append([name, title, purchase_sale, shares, date, disclosed_est])

    df = pd.DataFrame(data, columns=['Name', 'Title', 'Purchase/Sale', 'Shares', 'Date', 'Disclosed (EST)'])
    
    return df

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

def fetch_polygon_news(ticker, api_key=get_api_key("polygon_1")):
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
        
        news_data = []
        for article in articles:
            url = article.get('article_url', '')
            if url and "fool.com" in url.lower():
                continue
            
            title = article.get('title', 'No Title')
            published = article.get('published_utc', 'Unknown Date')
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

def drcr_sentiment_analysis(article_text):
    """
    Apply Dual Reverse Chain Reasoning (DRCR) for implicit sentiment analysis.
    Only the first 500 words of the article text are used.
    Returns a dictionary with:
      - 'dummy': the sentiment label ("positive", "negative", or "neutral")
      - 'score': the corresponding confidence score
    """
    words = article_text.split()[:500]
    truncated_text = ' '.join(words)
    
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
    
    pos_label = positive_reasoning['label'].lower()
    neg_label = negative_reasoning['label'].lower()
    
    pos_score = positive_reasoning['score'] if pos_label == 'positive' else 1 - positive_reasoning['score']
    neg_score = negative_reasoning['score'] if neg_label == 'negative' else 1 - negative_reasoning['score']
    
    if pos_score > neg_score:
        return {"dummy": "positive", "score": pos_score}
    elif neg_score > pos_score:
        return {"dummy": "negative", "score": neg_score}
    else:
        return {"dummy": "neutral", "score": (pos_score + neg_score) / 2}
    
def assign_news_score(static_df, news_df, tolerance='7D'):

    static_df['Traded Date'] = pd.to_datetime(static_df['Traded Date'], errors='coerce')
    news_df['Published'] = pd.to_datetime(news_df['Published'], errors='coerce')
    
    static_df_sorted = static_df.sort_values('Traded Date').reset_index(drop=True)
    news_df_sorted = news_df.sort_values('Published').reset_index(drop=True)
    
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

def drcr_sentiment(ticker, api_key = get_api_key("polygon_1")):
    df = fetch_polygon_news(ticker, api_key)
    df['Published'] = pd.to_datetime(df['Published'], errors='coerce').dt.strftime('%Y-%m-%d')
    df['result'] = df['Text'].apply(drcr_sentiment_analysis)
    # Expand the dictionary into two new columns: 'dummy' and 'score'
    df[['dummy', 'score']] = df['result'].apply(pd.Series)
    df = df.drop(columns=['result'])
    return df

insider_df = pd.DataFrame()
congress_df = pd.DataFrame()
sentiment_df = pd.DataFrame()
zacks_rank_df = pd.DataFrame()
fundamental_df = pd.DataFrame()
technical_df = pd.DataFrame()
fundamental_score_df = pd.DataFrame()

os.makedirs(f"test_data/{ticker}", exist_ok=True)

if USE_STATIC_COV == True:

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

    date_columns = ['Disclosed (EST)', 'Date', 'Traded Date', 'Filed Date']

    for col in date_columns:
        if col in insider_df.columns:
            insider_df[col] = pd.to_datetime(insider_df[col], errors='coerce').dt.strftime('%Y-%m-%d')
        if col in congress_df.columns:
            congress_df[col] = pd.to_datetime(congress_df[col], errors='coerce').dt.strftime('%Y-%m-%d')
    
    congress_df.rename(columns={'Politician Name': 'Name', 
                            'Politician Position': 'Title', 
                            'Filed Date': 'Disclosed (EST)'}, inplace=True)
    if 'Transaction Amount' in congress_df.columns:
        congress_df['Transaction Amount'] = congress_df['Transaction Amount'].apply(
            lambda x: int(re.search(r'\$(\d[\d,]*)$', x).group(1).replace(',', '')) 
            if isinstance(x, str) and re.search(r'\$(\d[\d,]*)$', x) else None
        )
    
    if 'Date' in insider_df.columns:
        traded_dates_list = insider_df['Date'].tolist()
        open_prices = get_stock_open_prices(ticker, traded_dates_list)
        insider_df['Open Price'] = open_prices

    insider_df.rename(columns={'Purchase/Sale': 'Transaction Type', 
                           'Politician Position': 'Title', 
                           'Date': 'Traded Date'}, inplace=True)
    if 'Shares' in insider_df.columns:
        insider_df['Shares'] = pd.to_numeric(insider_df['Shares'], errors='coerce')
        insider_df['Transaction Amount'] = insider_df['Shares'] * insider_df['Open Price']
    else:
        insider_df['Transaction Amount'] = None  # Default to None if Shares column is missing

    merged_df = pd.concat([congress_df, insider_df], ignore_index=True)
    merged_df.drop(columns=['Stock', 'Description', 'Shares', 'Open Price'], errors='ignore', inplace=True)
    merged_df_sorted = merged_df.sort_values(by=['Name', 'Title', 'Traded Date', 'Transaction Type'])

    combined_rows = []
    current_group = None
    total_amount = 0

    for _, row in merged_df_sorted.iterrows():
        if current_group and (current_group == (row['Name'], row['Title'], row['Traded Date'], row['Transaction Type'])):
            total_amount += row['Transaction Amount'] 
            last_disclosed = row['Disclosed (EST)']  
        else:
           
            if current_group:
                combined_rows.append({
                    'Name': current_group[0],
                    'Title': current_group[1],
                    'Traded Date': current_group[2],
                    'Transaction Type': current_group[3],
                    'Transaction Amount': total_amount,
                '   Disclosed (EST)': last_disclosed
                })

        current_group = (row['Name'], row['Title'], row['Traded Date'], row['Transaction Type'])
        total_amount = row['Transaction Amount']
        last_disclosed = row['Disclosed (EST)']

    if current_group:
        combined_rows.append({
            'Name': current_group[0],
            'Title': current_group[1],
            'Traded Date': current_group[2],
            'Transaction Type': current_group[3],
            'Transaction Amount': total_amount,
            'Disclosed (EST)': last_disclosed
        })

    insider_trades_df = pd.DataFrame(combined_rows)

    insider_trades_df['Traded Date'] = pd.to_datetime(insider_trades_df['Traded Date'])

    insider_trades_df = insider_trades_df.sort_values(by='Traded Date').reset_index(drop=True)

    insider_df = pd.read_csv(f"test_data/{ticker}/{ticker}_Insider_Trading.csv")
    insider_df['Date'] = pd.to_datetime(insider_df['Date'], format="%b %d, %Y").dt.strftime("%Y-%m-%d")
    congress_df = pd.read_csv(f"test_data/{ticker}/{ticker}_Congress_Trades.csv")

    date_columns = ['Disclosed (EST)', 'Date', 'Traded Date', 'Filed Date']

    for col in date_columns:
        if col in insider_df.columns:
            insider_df[col] = pd.to_datetime(insider_df[col], errors='coerce').dt.strftime('%Y-%m-%d')
        if col in congress_df.columns:
            congress_df[col] = pd.to_datetime(congress_df[col], errors='coerce').dt.strftime('%Y-%m-%d')

    congress_df.rename(columns={
        'Politician Name': 'Name', 
        'Politician Position': 'Title', 
        'Filed Date': 'Disclosed (EST)'
    }, inplace=True)

    congress_df['Transaction Amount'] = congress_df['Transaction Amount'].apply(
        lambda x: int(re.search(r'\$(\d[\d,]*)$', x).group(1).replace(',', '')) if isinstance(x, str) and re.search(r'\$(\d[\d,]*)$', x) else None
    )

    traded_dates_list = insider_df['Date'].dropna().unique().tolist()

    open_prices = get_stock_open_prices(ticker, traded_dates_list)

    open_price_map = dict(zip(traded_dates_list, open_prices))
    insider_df['Open Price'] = insider_df['Date'].map(open_price_map)

    insider_df.rename(columns={'Purchase/Sale': 'Transaction Type', 'Date': 'Traded Date'}, inplace=True)

    insider_df['Shares'] = pd.to_numeric(insider_df['Shares'], errors='coerce').fillna(0)
    insider_df['Open Price'] = pd.to_numeric(insider_df['Open Price'], errors='coerce').fillna(0)
    insider_df['Open Price'] = insider_df['Open Price'].round(1)
    insider_df['Transaction Amount'] = insider_df['Shares'] * insider_df['Open Price']

    insider_df.drop(columns=['Stock', 'Description', 'Shares'], errors='ignore', inplace=True)

    merged_df = pd.concat([congress_df, insider_df], ignore_index=True)

    merged_df_sorted = merged_df.sort_values(by=['Name', 'Title', 'Traded Date', 'Transaction Type'])

    combined_rows = []
    current_group = None
    total_amount = 0

    for _, row in merged_df_sorted.iterrows():
        if current_group and (current_group == (row['Name'], row['Title'], row['Traded Date'], row['Transaction Type'])):
            total_amount += row['Transaction Amount']  
            last_disclosed = row['Disclosed (EST)']  
        else:
            if current_group:
                combined_rows.append({
                    'Name': current_group[0],
                    'Title': current_group[1],
                    'Traded Date': current_group[2],
                    'Transaction Type': current_group[3],
                    'Transaction Amount': total_amount,
                    'Disclosed (EST)': last_disclosed
                })

            current_group = (row['Name'], row['Title'], row['Traded Date'], row['Transaction Type'])
            total_amount = row['Transaction Amount']
            last_disclosed = row['Disclosed (EST)']

    if current_group:
        combined_rows.append({
            'Name': current_group[0],
            'Title': current_group[1],
            'Traded Date': current_group[2],
            'Transaction Type': current_group[3],
            'Transaction Amount': total_amount,
            'Disclosed (EST)': last_disclosed
        })

    insider_trades_df = pd.DataFrame(combined_rows)

    insider_trades_df['Traded Date'] = pd.to_datetime(insider_trades_df['Traded Date'])
    insider_trades_df = insider_trades_df.sort_values(by='Traded Date').reset_index(drop=True)

    static_df = insider_trades_df

    if not sentiment_df.empty and 'general_sentiment_score' in sentiment_df.columns:
        latest_sentiment_score = sentiment_df['general_sentiment_score'].iloc[0]
        used_sentiment = True

    else:
        latest_sentiment_score = 0  
        used_sentiment = False

    latest_zacks_score = zacks_rank

    recent_cutoff = datetime.now() - timedelta(days=30)

    static_df["Traded Date"] = pd.to_datetime(static_df["Traded Date"])

    static_df["Zacks Score"] = static_df["Traded Date"].apply(
        lambda x: latest_zacks_score if x >= recent_cutoff else None
    )

    static_df["Sentiment Score"] = static_df["Traded Date"].apply(
        lambda x: latest_sentiment_score if x >= recent_cutoff else None
    )   
    static_df.to_csv(f"test_data/{ticker}/{ticker}_Static_Data.csv", index=False)

    static_df = static_df.drop(columns=['Zacks Score', 'Sentiment Score'], errors='ignore')

    static_df = pd.get_dummies(static_df, columns=['Transaction Type'], dtype=int)
    static_df = pd.get_dummies(static_df, columns=['Name'], dtype=int)

    title_encoder = LabelEncoder()
    if "Title" in static_df.columns:
        static_df['Title'] = title_encoder.fit_transform(static_df['Title'])
        static_df['Title'] = static_df['Title'].astype(int)

    if "Traded Date" in static_df.columns:
        static_df["Traded Date"] = pd.to_datetime(static_df["Traded Date"], errors="coerce")
    if "Disclosed (EST)" in static_df.columns:
        static_df["Disclosed (EST)"] = pd.to_datetime(static_df["Disclosed (EST)"], errors="coerce")

    if "Traded Date" in static_df.columns and "Disclosed (EST)" in static_df.columns:   
        static_df["Disclosure Delay"] = (static_df["Disclosed (EST)"] - static_df["Traded Date"]).dt.days

    if "Quarter_score" in static_df.columns and static_df["Quarter_score"].notna().any():   
        static_df["Quarter_score"] = static_df["Quarter_score"].astype(str).str.extract(r'(\d+)/\d+')
        static_df["Quarter_score"] = pd.to_numeric(static_df["Quarter_score"], errors='coerce').astype('Int64')
    else:   
    
        if "Traded Date" in static_df.columns:
            current_year = datetime.now().year
            static_df = static_df[static_df["Traded Date"].dt.year >= current_year - 1]
            print("'Quarter_score' is missing or empty. Using only data from the current and last year.")
        else:
            print("'Traded Date' is missing. Skipping year-based filtering.")

    static_df = static_df.drop(columns=["Disclosed (EST)"], errors="ignore")

    bool_cols = static_df.select_dtypes(include=bool).columns
    static_df[bool_cols] = static_df[bool_cols].astype(int)
    static_df = static_df.reset_index(drop=True)
    print("Data processing completed successfully.")

    static_covariates = pd.DataFrame(static_df.mean()).T

    MODEL_NAME = "ProsusAI/finbert"
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
    sentiment_pipeline = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

    news_df = drcr_sentiment(ticker, api_key = get_api_key("polygon_1"))
    static_with_news = assign_news_score(static_df, news_df, tolerance='7D')
    if used_sentiment:  
        static_with_news = static_with_news[static_with_news['News Score'] != 0].reset_index(drop=True)
    
    static_covariates = pd.DataFrame(static_with_news.mean()).T

insider_df.to_csv(f"test_data/{ticker}/{ticker}_Insider_Trading.csv", index=False)
print('congress')
congress_df.to_csv(f"test_data/{ticker}/{ticker}_Congress_Trades.csv", index=False)
print('sentiment')
sentiment_df.to_csv(f"test_data/{ticker}/{ticker}_Sentiment_Data.csv", index=False)
print('zacks')
zacks_rank_df.to_csv(f"test_data/{ticker}/{ticker}_Zacks_Rank.csv", index=False)
print('fundamental')
fundamental_score_df.to_csv(f"test_data/{ticker}/{ticker}_Fundamental_Score.csv", index=False)

technical_df = technical_polygon(symbol = ticker, interval = interval, interval_range = interval_range, days = days)
technical_df.to_csv(f"test_data/{ticker}/{ticker}_Technical_Data.csv", index=False)


long_technical_df = technical_polygon(symbol = ticker, interval = interval, interval_range = long_interval_range, days = long_days)

live_df = technical_df
live_df.reset_index(inplace=True)
live_df.to_csv(f"test_data/{ticker}/{ticker}_Live_Data.csv", index=False)

live_df = pd.read_csv(f"test_data/{ticker}/{ticker}_Live_Data.csv")
stock_live_df = pd.read_csv(f"test_data/{ticker}/{ticker}_Live_Data.csv")

live_df = live_df.loc[:, : 'Stochastic']
stock_live_df = stock_live_df.loc[:, : 'Stochastic']

live_df['y'] = live_df['close'].shift(-10)
live_df = live_df.iloc[::-1].reset_index(drop=True)

long_technical_df.to_csv(f"test_data\\{ticker}\\{ticker}_Long_Technical_Data.csv", index=False)

long_live_df = long_technical_df
long_live_df.reset_index(inplace=True)
long_live_df.to_csv(f"test_data\\{ticker}\\{ticker}_Long_Live_Data.csv", index=False)

long_live_df = pd.read_csv(f"test_data\\{ticker}\\{ticker}_Long_Live_Data.csv")
long_stock_live_df = pd.read_csv(f"test_data\\{ticker}\\{ticker}_Long_Live_Data.csv")

long_live_df = long_live_df.loc[:, : 'Stochastic']
long_stock_live_df = long_stock_live_df.loc[:, : 'Stochastic']

long_live_df['y'] = long_live_df['close'].shift(-10)
long_live_df = long_live_df.iloc[::-1].reset_index(drop=True)

def getXY(df1, forecasting_horizon, freq = '5min', freq_code = '5T'):
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
    '''
    Timeframe	freq value
    15 minutes	"15min" or "15T"
    30 minutes	"30min" or "30T"
    1 hour	    "60min" or "1H"
    1 day	    "1D"
    '''

    df = df1.copy()
    
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df.set_index('timestamp', inplace=True)
    
    df = df.resample(freq_code).asfreq()
    df.fillna(method='ffill', inplace=True)
    
    df = df.reset_index()
    
    df['y'] = df['close'].shift(-forecasting_horizon)
    
    df = df.iloc[:-forecasting_horizon].copy()
    
    # xdf contains all features, and ydf holds only the target 'y' with its timestamp.
    xdf = df.copy()
    ydf = df[['timestamp', 'y']].copy()
    
    # Build TimeSeries objects:
    y_series = TimeSeries.from_dataframe(ydf,
                                         time_col='timestamp',
                                         value_cols='y',
                                         freq=freq,
                                         fill_missing_dates=True)
    cov_cols = [col for col in xdf.columns if col not in ['timestamp', 'y']]
    X_series = TimeSeries.from_dataframe(xdf,
                                         time_col='timestamp',
                                         value_cols=cov_cols,
                                         freq=freq,
                                         fill_missing_dates=True)
    
    return X_series, y_series, xdf, ydf

X_series, y_series, xdf, ydf = getXY(live_df, forecasting_horizon)

X_series, y_series, xdf, ydf = getXY(live_df, forecasting_horizon)
xdf['y'] = ydf['y'].values

if USE_STATIC_COV == True:
    series = TimeSeries.from_dataframe(xdf,
                                   value_cols = 'y',
                                   time_col = 'timestamp',
                                   fill_missing_dates=True,
                                    freq="5min",
                                   static_covariates = static_covariates)
if USE_STATIC_COV == False:
    series = TimeSeries.from_dataframe(xdf,
                                   value_cols = 'y',
                                   time_col = 'timestamp',
                                   fill_missing_dates=True,
                                    freq="5min")

scaler1 = Scaler()
scaler2 = Scaler()

# Step 1: Transform
y_transformed = scaler1.fit_transform(y_series)
past_covariates_transformed = scaler2.fit_transform(series)



long_X_series, long_y_series, long_xdf, long_ydf = getXY(long_live_df, forecasting_horizon,  freq = '30min', freq_code = '30T')

# Ensure y is attached to xdf
long_xdf['y'] = long_ydf['y'].values

# Build TimeSeries object (with or without static covariates)
if USE_STATIC_COV:
    long_series = TimeSeries.from_dataframe(
        long_xdf,
        value_cols='y',
        time_col='timestamp',
        fill_missing_dates=True,
        freq="30min",
        static_covariates=static_covariates
    )
else:
    long_series = TimeSeries.from_dataframe(
        long_xdf,
        value_cols='y',
        time_col='timestamp',
        fill_missing_dates=True,
        freq="30min"
    )

# Scalers for target and covariates
long_scaler1 = Scaler()
long_scaler2 = Scaler()

# Apply transformations
long_y_transformed = long_scaler1.fit_transform(long_y_series)
long_past_covariates_transformed = long_scaler2.fit_transform(long_series)
# Helper function to process a transformed series
def prepare_series(transformed_series, final_len=None):
    if isinstance(transformed_series, pd.DataFrame):
        df = transformed_series
    else:
        df = transformed_series.pd_dataframe()
    df = df.ffill().bfill()
    if final_len is not None:
        df = df.iloc[-final_len:]
    ts = TimeSeries.from_dataframe(df).astype('float32')
    return df, ts

# Step 2: Apply to each case
y_transformed_df, y_transformed_clean = prepare_series(y_transformed, final_len=7506)
past_covariates_transformed_df, past_covariates_transformed_clean = prepare_series(past_covariates_transformed, final_len=17157)

long_y_transformed_df, long_y_transformed_clean = prepare_series(long_y_transformed, final_len=7506)
long_past_covariates_transformed_df, long_past_covariates_transformed_clean = prepare_series(long_past_covariates_transformed, final_len=17157)

def encode_hour(idx):
    return idx.hour / 24

add_encoders = {
    'cyclic': {'future': ['hour', 'day', 'dayofweek', 'week', 'month']},
    'datetime_attribute': {'future': ['hour', 'day', 'dayofweek', 'week', 'month']},
    'position': {'past': ['relative'], 'future': ['relative']},
    'custom': {'past': [encode_hour], 'future': [encode_hour]},
    'transformer': Scaler(),
    'tz': 'CET'
}

best_params_df = pd.read_csv(f'NVDA/NVDA_best_params.csv')
best_params = best_params_df.iloc[0]

if USE_STATIC_COV == False:
    best_params_dict = {
        'output_chunk_length': 5,
        'num_attention_heads': int(best_params['num_attention_heads']),
        'n_epochs': int(best_params['n_epochs']),
        'lstm_layers': int(best_params['lstm_layers']),
        'input_chunk_length': int(best_params['input_chunk_length']),
        'hidden_size': int(best_params['hidden_size']),
        'dropout': float(best_params['dropout']),
        'batch_size': int(best_params['batch_size']),
        'use_static_covariates': False,
        'add_encoders': add_encoders,
        'pl_trainer_kwargs': {'accelerator': 'cpu'}  # Adjust as needed
    }

# Build and train the model
model = TFTModel(**best_params_dict)
long_model = TFTModel(**best_params_dict)

model.fit(
    y_transformed_clean,
    past_covariates=past_covariates_transformed_clean
)

long_model.fit(
    long_y_transformed_clean,
    past_covariates=long_past_covariates_transformed_clean
)

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

# ─────────────────────────────────────────────────────────────────────────────
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

ALPHA_KEY = get_api_key("alpha")

def get_price_from_alpha(symbol: str,
                         interval: str = "1min",
                         output_size: str = "compact") -> float:
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_INTRADAY",
        "symbol": symbol,
        "interval": interval,
        "apikey": ALPHA_KEY,
        "outputsize": output_size,
    }
    r = requests.get(url, params=params, timeout=5)
    data = r.json()
    ts = data.get(f"Time Series ({interval})")
    if not ts:
        raise RuntimeError(f"No intraday data for {symbol}")
    latest = sorted(ts.keys())[-1]
    return float(ts[latest]["4. close"])

def append_to_df(ticker, df, api_key=get_api_key("twelvedata"), interval="1min", outputsize=200):
    # Get the last N rows
    new_data = get_twelvedata_last_n_minutes(ticker, api_key, interval, outputsize)
    combined_df = pd.concat([df, new_data], ignore_index=True).drop_duplicates(subset="timestamp").sort_values("timestamp").reset_index(drop=True)
    
    print(f"{len(new_data)} new rows merged.")
    return combined_df

from datetime import datetime

os.makedirs("model_checkpoints", exist_ok=True)
today_str = datetime.now().strftime('%d.%m.%Y')

model.save(f"model_checkpoints/tft_PPL({today_str})_model.pt")
long_model.save(f"model_checkpoints/tft_long_PPL({today_str}))_model.pt")

model_b_day = datetime.now()

















########################################################################3













# ─────────────────────────────────────────────────────────────────────────────
def is_market_open():
    """Check if the market is currently open using Polygon.io."""
    api_key = get_api_key('polygon_2')
    url = f"https://api.polygon.io/v1/marketstatus/now?apiKey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get("market", "closed") == "open"
    return False
# ─────────────────────────────────────────────────────────────────────────────
from concurrent.futures import ThreadPoolExecutor
import threading
import time
import datetime
import yfinance as yf
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order
from ibapi.execution import ExecutionFilter
#best = {'Symbol' : 'NVDA'}
# === Custom IB API wrapper ===
class IBApi(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.connected_evt = threading.Event()
        self.nextOrderId = None
        self.account_values = []
        self.exec_details = []

    def nextValidId(self, orderId: int):
        self.nextOrderId = orderId
        self.connected_evt.set()
        print(f"[IB] Next valid order ID: {orderId}")

    def accountSummary(self, reqId, account, tag, value, currency):
        if tag == 'NetLiquidation':
            self.account_values.append((datetime.datetime.now(), float(value)))

    def execDetails(self, reqId, contract, execution):
        self.latest_price = execution.price
        self.execution_completed.set() 
        self.exec_details.append({
            "symbol": contract.symbol,
            "action": execution.side,
            "qty": execution.shares,
            "price": execution.avgPrice,
            "time": datetime.datetime.now()
        })

    def error(self, reqId, errorCode, errorString):
        print(f"[ERROR] reqId={reqId} code={errorCode} msg={errorString}")

# === IBKR Trading Bot === # ─────────────────────────────────────────────────────────────────────────────
class IBTradingBot:
    def __init__(self, usd_amount=150.0):
        self.ib = IBApi()
        self.clientId = 1
        self.port = 7496
        self.host = "127.0.0.1"
        self.pos = 0
        self.default_usd_amount = usd_amount

    def connect(self, clientId=1):
        self.ib.connect(self.host, self.port, clientId)
        threading.Thread(target=self.ib.run, daemon=True).start()
        if not self.ib.connected_evt.wait(5):
            raise RuntimeError("No nextValidId received")

    def disconnect(self):
        self.ib.disconnect()

    def make_contract(self, symbol):
        c = Contract()
        c.symbol = symbol
        c.secType = "STK"
        c.exchange = "SMART"
        c.primaryExchange = "ISLAND"
        c.currency = "USD"
        return c

    def get_excess_liquidity(self):
        self.ib.account_values = []
        self.request_account_value()
        if self.ib.account_values:
            try:
                return float(self.ib.account_values[-1][1])  # NetLiquidation as float
            except (IndexError, ValueError):
                print("[ERROR] Could not parse NetLiquidation.")
        return 0

    def place_market_order(self, symbol, action):
        try:
            contract = self.make_contract(symbol)

            net_liq = self.get_excess_liquidity()
            max_usd = max(net_liq - 10, 0)

            yf_data = yf.Ticker(symbol)
            market_price = yf_data.info.get("regularMarketPrice", 100.0)

            if market_price <= 0:
                raise ValueError("Invalid market price received")

            qty = max(int(max_usd // market_price), 1)
            print(f"[ORDER] Action={action} Qty={qty} MaxUSD={max_usd:.2f} Price={market_price:.2f}")

            oid = self.ib.nextOrderId
            self.ib.nextOrderId += 1

            order = Order()
            order.action = action
            order.orderType = "MKT"
            order.totalQuantity = qty
            order.tif = "DAY"
            order.transmit = True

            order.eTradeOnly = False
            order.firmQuoteOnly = False

            self.ib.exec_details = []
            self.ib.placeOrder(oid, contract, order)

            for _ in range(5):
                time.sleep(1)
                if self.ib.exec_details:
                    break

            if not self.ib.exec_details:
                print("[RETRY] Order not filled, retrying once")
                retry_oid = self.ib.nextOrderId
                self.ib.nextOrderId += 1
                self.ib.placeOrder(retry_oid, contract, order)
                time.sleep(5)

            if self.ib.exec_details:
                print(f"[EXECUTED] {action} order filled.")
                self.pos = 1 if action == "BUY" else 0
            else:
                print("[FAIL] Order was not filled after retry.")

        except Exception as e:
            print(f"[ERROR] Failed to place market order: {e}")

    def buy(self, s):
        self.execution_completed.clear()  # Reset before placing order
        self.place_market_order(s, "BUY")
    
        # Wait for price to be received
        if self.execution_completed.wait(timeout=10):  # wait max 10 seconds
            return self.latest_price
        else:
            print("Execution price not received in time.")
            return None

    def close_buy(self, s):
        self.place_market_order(s, "SELL")
        
    def request_account_value(self):
        self.ib.reqAccountSummary(9001, "All", "NetLiquidation")
        time.sleep(2)
        self.ib.cancelAccountSummary(9001)

    def request_executions(self):
        f = ExecutionFilter()
        f.time = (datetime.datetime.now() - datetime.timedelta(days=360)).strftime("%Y%m%d-%H:%M:%S")
        self.ib.reqExecutions(9002, f)
        time.sleep(2)
        
    def request_account_value(self):
        self.ib.reqAccountSummary(9001, "All", "NetLiquidation")
        time.sleep(2)
        self.ib.cancelAccountSummary(9001)

    def request_executions(self):
        f = ExecutionFilter()
        f.time = (datetime.datetime.now() - datetime.timedelta(days=360)).strftime("%Y%m%d-%H:%M:%S")
        self.ib.reqExecutions(9002, f)
        time.sleep(2)

    def fetch_ticker_info(self, ticker):
        tk = yf.Ticker(ticker)
        info = tk.info
        return {
            "Price": info.get("regularMarketPrice", "N/A"),
            "Bid": info.get("bid", "N/A"),
            "Ask": info.get("ask", "N/A"),
            "EPS": info.get("trailingEps", "N/A"),
            "Market Cap": info.get("marketCap", "N/A"),
            "P/E": info.get("trailingPE", "N/A"),
            "Sector": info.get("sector", "N/A"),
            "Industry": info.get("industry", "N/A")
        }

    def generate_eod_report(self, filename="eod_report.pdf", ticker="AAPL"):
        self.request_account_value()
        self.request_executions()

        df = pd.DataFrame(self.ib.account_values, columns=["Timestamp", "NetLiquidation"])
        df["Timestamp"] = pd.to_datetime(df["Timestamp"])
        df["Shift"] = df["NetLiquidation"].shift(1)
        df2 = df[df["NetLiquidation"] != df["Shift"]].copy()

        plt.figure(figsize=(10, 4))
        if len(df2) > 1:
            plt.plot(df2["Timestamp"], df2["NetLiquidation"], marker="o", color="blue")
        else:
            val = df["NetLiquidation"].iloc[-1]
            plt.axhline(val, linestyle="--", color="gray")
        plt.title("Net Liquidation")
        plt.xlabel("Time")
        plt.ylabel("USD")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig("equity.png")
        plt.close()

        info = self.fetch_ticker_info(ticker)
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "EOD Report", ln=True)
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, f"Generated: {datetime.datetime.now():%Y-%m-%d %H:%M:%S}", ln=True)
        pdf.ln(5)
        pdf.image("equity.png", w=120)

        pdf.set_xy(135, 30)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, f"Ticker: {ticker}", ln=True)
        pdf.set_font("Arial", "", 11)
        for k, v in info.items():
            pdf.set_x(135)
            pdf.cell(0, 6, f"{k}: {v}", ln=True)
        pdf.ln(10)

        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Executions:", ln=True)
        df_exec = pd.DataFrame(self.ib.exec_details)
        if not df_exec.empty:
            df_exec["time"] = pd.to_datetime(df_exec["time"], errors="coerce")
            df_exec = df_exec.sort_values("time", ascending=False)
            pdf.set_font("Arial", "", 10)
            col_w = [20, 20, 20, 25, 60]
            headers = ["symbol", "action", "qty", "price", "time"]
            for i, h in enumerate(headers):
                pdf.cell(col_w[i], 8, h.title(), border=1)
            pdf.ln()
            for _, r in df_exec.iterrows():
                pdf.cell(col_w[0], 8, str(r.symbol), border=1)
                pdf.cell(col_w[1], 8, str(r.action), border=1)
                pdf.cell(col_w[2], 8, str(r.qty), border=1)
                pdf.cell(col_w[3], 8, f"{r.price:.2f}", border=1)
                pdf.cell(col_w[4], 8, str(r.time)[:19], border=1)
                pdf.ln()

        pdf.output(filename)
        os.remove("equity.png")
        print(f"[PDF] Saved {filename}")

    def execDetails(self, reqId, contract, execution):
        self.exec_details.append({
            "execId": execution.execId,
            "symbol": contract.symbol,
            "action": execution.side,
            "qty": execution.shares,
            "price": execution.avgPrice,
            "time": datetime.datetime.now()
        })
    
    def commissionReport(self, commissionReport):
        print(f"[COMMISSION] Received: {commissionReport.commission} {commissionReport.currency} on {commissionReport.execId}")
        self.exec_details[-1]["commission"] = commissionReport.commission

    def get_commission_percentage(self):
        if not self.ib.exec_details:
            print("[INFO] No execution details to compute commission.")
            return

        for detail in self.ib.exec_details:
            if "commission" in detail:
                total_value = detail["qty"] * detail["price"]
                commission = detail["commission"]
                pct = (commission / total_value) * 100 if total_value > 0 else 0
                print(f"[RESULT] {detail['action']} {detail['qty']} @ {detail['price']:.2f}")
                print(f"         Commission: {commission:.2f} USD")
                print(f"         Commission %: {pct:.4f}%")
            else:
                print(f"[WAIT] Commission not received yet for execId={detail['execId']}")

    def request_account_value(self):
        self.ib.reqAccountSummary(9001, "All", "NetLiquidation")
        time.sleep(2)
        self.ib.cancelAccountSummary(9001)

    def request_executions(self):
        f = ExecutionFilter()
        f.time = (datetime.datetime.now() - datetime.timedelta(days=360)).strftime("%Y%m%d-%H:%M:%S")
        self.ib.reqExecutions(9002, f)
        time.sleep(2)

    def fetch_ticker_info(self, ticker):
        tk = yf.Ticker(ticker)
        info = tk.info
        return {
            "Price": info.get("regularMarketPrice", "N/A"),
            "Bid": info.get("bid", "N/A"),
            "Ask": info.get("ask", "N/A"),
            "EPS": info.get("trailingEps", "N/A"),
            "Market Cap": info.get("marketCap", "N/A"),
            "P/E": info.get("trailingPE", "N/A"),
            "Sector": info.get("sector", "N/A"),
            "Industry": info.get("industry", "N/A")
        }

    def generate_eod_report(self, filename="eod_report.pdf", ticker="AAPL"):
        self.request_account_value()
        self.request_executions()
        df = pd.DataFrame(self.ib.account_values, columns=["Timestamp","NetLiquidation"])
        df["Timestamp"] = pd.to_datetime(df["Timestamp"])
        df["Shift"] = df["NetLiquidation"].shift(1)
        df2 = df[df["NetLiquidation"] != df["Shift"]].copy()
        plt.figure(figsize=(10,4))
        if len(df2) > 1:
            plt.plot(df2["Timestamp"], df2["NetLiquidation"], marker="o", color="blue")
        else:
            val = df["NetLiquidation"].iloc[-1]
            plt.axhline(val, linestyle="--", color="gray")
        plt.title("Net Liquidation")
        plt.xlabel("Time"); plt.ylabel("USD"); plt.grid(True)
        plt.tight_layout()
        plt.savefig("equity.png"); plt.close()

        info = self.fetch_ticker_info(ticker)
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial","B",16); pdf.cell(0,10,"EOD Report",ln=True)
        pdf.set_font("Arial","",12); pdf.cell(0,10,f"Generated: {datetime.datetime.now():%Y-%m-%d %H:%M:%S}",ln=True)
        pdf.ln(5)
        pdf.image("equity.png", w=120)

        # Ticker info on right
        pdf.set_xy(135, 30)
        pdf.set_font("Arial","B",12); pdf.cell(0,8,f"Ticker: {ticker}", ln=True)
        pdf.set_font("Arial","",11)
        for k,v in info.items():
            pdf.set_x(135); pdf.cell(0,6,f"{k}: {v}", ln=True)
        pdf.ln(10)

        # Executions table
        pdf.set_font("Arial","B",14); pdf.cell(0,10,"Executions :",ln=True)
        df_exec = pd.DataFrame(self.ib.exec_details)
        if "time" in df_exec.columns:
            df_exec["time"] = pd.to_datetime(df_exec["time"], errors="coerce")
            df_exec = df_exec.sort_values("time", ascending=False)
        pdf.set_font("Arial","",10)
        col_w = [20,20,20,25,60]
        for h in ["symbol","action","qty","price","time"]:
            pdf.cell(col_w[["symbol","action","qty","price","time"].index(h)], 8, h.title(), border=1)
        pdf.ln()
        for _,r in df_exec.iterrows():
            pdf.cell(col_w[0],8,r.symbol,border=1)
            pdf.cell(col_w[1],8,r.action,border=1)
            pdf.cell(col_w[2],8,str(r.qty),border=1)
            pdf.cell(col_w[3],8,f"{r.price:.2f}",border=1)
            pdf.cell(col_w[4],8,str(r.time)[:19],border=1)
            pdf.ln()

        pdf.output(filename)
        os.remove("equity.png")
        print(f"[PDF] Saved {filename}")

class IBCommissionAnalyzer:
    def __init__(self, usd_amount=50.0):
        self.ib = IBApi()
        self.usd_amount = usd_amount
        self.host = "127.0.0.1"
        self.port = 7496
        self.clientId = 1

    def connect(self):
        self.ib.connect(self.host, self.port, self.clientId)
        threading.Thread(target=self.ib.run, daemon=True).start()
        if not self.ib.connected_evt.wait(5):
            raise RuntimeError("Failed to connect to IB Gateway")

    def disconnect(self):
        self.ib.disconnect()

    def get_market_price(self, symbol):
        data = yf.Ticker(symbol)
        price = data.info.get("regularMarketPrice", None)
        if price is None or price <= 0:
            raise ValueError("Could not fetch market price.")
        return price

    def estimate_required_gain_pct(self, symbol):
        price = self.get_market_price(symbol)
        qty = int(self.usd_amount // price)

        if qty < 1:
            raise ValueError("Not enough capital to buy 1 share.")

        trade_value = qty * price

        # Commission rules:
        if trade_value < 30:
            commission = trade_value * 0.01  # 1% rule
        else:
            commission = max(qty * 0.0035, 0.35)  # Tiered pricing fallback

        required_pct_gain = (commission / trade_value) * 100

        print(f"\n[COMMISSION ANALYSIS] for {symbol}")
        print(f"  Price: ${price:.2f}")
        print(f"  Qty: {qty} → Trade value: ${trade_value:.2f}")
        print(f"  Commission estimate: ${commission:.4f}")
        print(f"  ➤ Required stock gain to break even: {required_pct_gain:.4f}%")

        return required_pct_gain

def train_train_model(live_df, ticker, forecasting_horizon, static_covariates=None, USE_STATIC_COV=False):

    start_time = time.time()

    # Preprocessing
    live_df = technical_indicators(live_df)
    live_df.reset_index(inplace=True)
    live_df = live_df.sort_values('timestamp').reset_index(drop=True)
    live_df['y'] = live_df['close']
    live_df.dropna(inplace=True)

    # ---------------- GetXY ---------------- #
    def getXY(df1, forecasting_horizon, freq='5min', freq_code='5T'):
        df = df1.copy()
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        df.set_index('timestamp', inplace=True)
        df = df.resample(freq_code).asfreq().fillna(method='ffill').reset_index()
        df['y'] = df['close'].shift(-forecasting_horizon)
        df = df.iloc[:-forecasting_horizon].copy()
        xdf = df.copy()
        ydf = df[['timestamp', 'y']].copy()
        cov_cols = [col for col in xdf.columns if col not in ['timestamp', 'y']]
        y_series = TimeSeries.from_dataframe(ydf, time_col='timestamp', value_cols='y', freq=freq, fill_missing_dates=True)
        X_series = TimeSeries.from_dataframe(xdf, time_col='timestamp', value_cols=cov_cols, freq=freq, fill_missing_dates=True)
        return X_series, y_series, xdf, ydf

    # Create transformed TimeSeries
    X_series, y_series, xdf, ydf = getXY(live_df, forecasting_horizon)
    xdf['y'] = ydf['y'].values

    series = TimeSeries.from_dataframe(
        xdf,
        value_cols='y',
        time_col='timestamp',
        fill_missing_dates=True,
        freq="5min",
        static_covariates=static_covariates if USE_STATIC_COV else None
    )

    scaler1, scaler2 = Scaler(), Scaler()
    y_transformed = scaler1.fit_transform(y_series)
    past_covariates_transformed = scaler2.fit_transform(series)

    def prepare_series(transformed_series, final_len=None):
        df = transformed_series.pd_dataframe().fillna(method='ffill').fillna(method='bfill')
        if final_len is not None:
            df = df.iloc[-final_len:]
        return df, TimeSeries.from_dataframe(df).astype('float32')

    y_transformed_df, y_transformed_clean = prepare_series(y_transformed, final_len=7506)
    past_covariates_transformed_df, past_covariates_transformed_clean = prepare_series(past_covariates_transformed, final_len=17157)

    # ---------------- Define Model ---------------- #
    def encode_hour(idx):
        return idx.hour / 24

    add_encoders = {
        'cyclic': {'future': ['hour', 'day', 'dayofweek', 'week', 'month']},
        'datetime_attribute': {'future': ['hour', 'day', 'dayofweek', 'week', 'month']},
        'position': {'past': ['relative'], 'future': ['relative']},
        'custom': {'past': [encode_hour], 'future': [encode_hour]},
        'transformer': Scaler(),
        'tz': 'CET'
    }

    #best_params_df = pd.read_csv(f'{ticker}/{ticker}_best_params.csv')
    #best_params = best_params_df.iloc[0]

    best_params_dict = { 
        'output_chunk_length': 5,
        'num_attention_heads': int(best_params['num_attention_heads']),
        'n_epochs': int(best_params['n_epochs']),
        'lstm_layers': int(best_params['lstm_layers']),
        'input_chunk_length': int(best_params['input_chunk_length']),
        'hidden_size': int(best_params['hidden_size']),
        'dropout': float(best_params['dropout']),
        'batch_size': int(best_params['batch_size']),
        'use_static_covariates': USE_STATIC_COV,
        'add_encoders': add_encoders,
        'pl_trainer_kwargs': {'accelerator': 'cpu'}
    }

    # Train models
    model = TFTModel(**best_params_dict)
    model.fit(y_transformed_clean, past_covariates=past_covariates_transformed_clean)

    end_time = time.time()
    elapsed_seconds = round(end_time - start_time, 2)

    return model,  elapsed_seconds

import json

def save_signal_to_json(signal, filename="signal_log.json"):
    data = {
        "timestamp": datetime_o.now().strftime("%Y-%m-%d %H:%M:%S"),
        "signal": bool(signal)  # <-- force conversion to native bool
    }
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)
    print(f"[JSON] Signal saved: {data}")

def get_live_stock_data(ticker: str, api_key: str = get_api_key('twelvedata'), interval='1min', max_records: int = 5000) -> pd.DataFrame:
    url = f"https://api.twelvedata.com/time_series?symbol={ticker}&interval={interval}&apikey={api_key}&outputsize={max_records}"
    response = requests.get(url).json()

    if "values" not in response:
        raise Exception("Error fetching live data: " + str(response))

    latest = response["values"]  # list of dicts

    df = pd.DataFrame([{
        "timestamp": pd.to_datetime(entry["datetime"]),
        "open": float(entry["open"]),
        "high": float(entry["high"]),
        "low": float(entry["low"]),
        "close": float(entry["close"]),
        "volume": float(entry["volume"]),
    } for entry in latest])

    df = df.sort_values("timestamp").reset_index(drop=True)
    return df
    
def get_hourly_stock_data(ticker: str, api_key: str = get_api_key('twelvedata'), max_records: int = 5000) -> pd.DataFrame:
    interval = '1h'
    url = (
        f"https://api.twelvedata.com/time_series"
        f"?symbol={ticker}&interval={interval}&outputsize={max_records}&apikey={api_key}"
    )
    
    response = requests.get(url).json()

    if "values" not in response:
        raise Exception("Error fetching data: " + str(response))

    df = pd.DataFrame([{
        "timestamp": pd.to_datetime(entry["datetime"]),
        "open": float(entry["open"]),
        "high": float(entry["high"]),
        "low": float(entry["low"]),
        "close": float(entry["close"]),
        "volume": float(entry["volume"]),
    } for entry in response["values"]])

    df = df.sort_values("timestamp").reset_index(drop=True)
    return df

def buy_signal(n_df, model, min_df, forecasting_horizon, static_covariates=None, 
               long_n_df=None, long_model=None, n=5, first_pred=False):
    
    def markov_adaptation(forecast_pct, real_pct):
        def classify(x):
            if x > 0.0005: return "UP"
            elif x < -0.0005: return "DOWN"
            else: return "FLAT"

        from collections import defaultdict

        def build_chain(states):
            chain = defaultdict(lambda: defaultdict(int))
            for (s1, s2) in zip(states[:-1], states[1:]):
                chain[s1][s2] += 1
            for s1 in chain:
                total = sum(chain[s1].values())
                for s2 in chain[s1]:
                    chain[s1][s2] /= total
            return chain

        def predict_seq(chain, start_state, steps):
            result = [start_state]
            current = start_state
            for _ in range(steps - 1):
                next_states = list(chain[current].keys())
                if not next_states:
                    break
                probs = list(chain[current].values())
                current = np.random.choice(next_states, p=probs)
                result.append(current)
            return result

        real_states = [classify(p) for p in real_pct]
        chain = build_chain(real_states)
        forecast_states = [classify(p) for p in forecast_pct]
        adapted_states = predict_seq(chain, forecast_states[-1], len(forecast_states))
        mapping = {"UP": 0.001, "DOWN": -0.001, "FLAT": 0.0}
        return pd.Series([mapping[s] for s in adapted_states]).cumsum()

    # === Preprocessing short horizon ===
    def preprocess(n_df, model, forecasting_horizon, static_covariates):
        n_df = technical_indicators(n_df)
        n_df.reset_index(inplace=True)
        n_df = n_df.sort_values('timestamp').reset_index(drop=True)
        n_df['y'] = n_df['close']
        n_df.dropna(inplace=True)

        if n_df['timestamp'].iloc[-1] < n_df['timestamp'].iloc[0]:
            n_df = n_df.iloc[::-1].reset_index(drop=True)

        if static_covariates is None:
            series = TimeSeries.from_dataframe(n_df, time_col='timestamp', value_cols='y', freq="5min").astype("float32")
        else:
            series = TimeSeries.from_dataframe(n_df, time_col='timestamp', value_cols='y', freq="5min", static_covariates=static_covariates).astype("float32")

        scaler = Scaler()
        past_covariates = scaler.fit_transform(series)

        # Pad if needed
        required_end = pd.Timestamp("2025-03-11 14:30:00")
        current_end = past_covariates.end_time()
        freq = pd.Timedelta(minutes=5)
        if current_end < required_end:
            extra_steps = int(((required_end - current_end).total_seconds() / 300) + 1)
            last_val = past_covariates.last_value()
            extra_times = pd.date_range(start=current_end + freq, periods=extra_steps, freq="5T")
            extra_series = TimeSeries.from_times_and_values(extra_times, [last_val] * extra_steps)
            past_covariates = past_covariates.concatenate(extra_series)

        past_covariates = past_covariates.astype("float32")

        forecast = model.predict(n=forecasting_horizon, series=series, past_covariates=past_covariates)
        forecast_values = scaler.inverse_transform(forecast).values().flatten()
        forecast_df = pd.DataFrame({"forecast_values": forecast_values})

        last_real_close = n_df['close'].iloc[-1] #confirmed value
        forecast_pct = pd.Series(forecast_values).pct_change().fillna(0).cumsum() #forecasted value
        real_pct = n_df['close'].pct_change().fillna(0).cumsum()

        adapted_pct = markov_adaptation(forecast_pct, real_pct)
        adapted_prices = last_real_close * (1 + adapted_pct)
        forecast_df["forecast_values"] = adapted_prices.values

        return forecast_df, n_df

    # === Run short model
    forecast_df, n_df = preprocess(n_df, model, forecasting_horizon, static_covariates)
    print(forecast_df)
    if len(forecast_df) < n:
        print(f"[WARN] Not enough forecasted values. Expected: {n}, Got: {len(forecast_df)}")
        return False

    trend_confirmed, rsi_divergence = calculate_adx_rsi(min_df, high_col="high", low_col="low", close_col="close")
    transition_matrix = make_markov_chain_transition_matrix(n_df, close_column_name="close")
    trend = predict_next_trend(n_df["Trend"].iloc[-1], transition_matrix)

    close_diff = abs(n_df['close'].iloc[1] - n_df['close'].iloc[0]) / n_df['close'].iloc[0]
    forecast_diff = abs(forecast_df['forecast_values'].iloc[1] - forecast_df['forecast_values'].iloc[0]) / forecast_df['forecast_values'].iloc[0]
    first_a = close_diff < forecast_diff

    latest_close = n_df['close'].iloc[-1]
    highest_forecast = forecast_df['forecast_values'].max()
    newest_forecast = forecast_df['forecast_values'].iloc[0]
    price_change = (highest_forecast - newest_forecast) / newest_forecast

    print(f"Forecasted value @ step {n}: {newest_forecast}, Latest close: {latest_close}")
    print(f"Price change (%): {price_change * 100:.2f}%")

    if price_change > 0.006:
        predicted = forecast_df['forecast_values'].iloc[0]
        print(f"[BUY LOG] Predicted: {predicted}, Actual: {min_df['close'].iloc[-1]}")

    # === Long model (if provided) ===
    long_price_change = None
    if long_n_df is not None and long_model is not None:
        long_forecast_df, long_n_df = preprocess(long_n_df, long_model, forecasting_horizon, static_covariates)
        long_latest_close = long_n_df['close'].iloc[-1]
        long_highest_forecast = long_forecast_df['forecast_values'].max()
        long_min_forecast = long_forecast_df['forecast_values'].min()
        long_price_change = (long_highest_forecast - long_min_forecast) / long_min_forecast

        print(f"[LONG] Forecasted minvalue : {long_min_forecast}, Latest close: {long_latest_close}")
        print(f"[LONG] Price change (%): {long_price_change * 100:.2f}%")

    return price_change, long_price_change, long_highest_forecast


def background_training():
    return train_train_model(df_15min, ticker, forecasting_horizon=10, USE_STATIC_COV=False)
    
def get_hourly_stock_data(ticker: str, api_key: str = get_api_key('twelvedata'), max_records: int = 5000) -> pd.DataFrame:
    interval = '1h'
    url = (
        f"https://api.twelvedata.com/time_series"
        f"?symbol={ticker}&interval={interval}&outputsize={max_records}&apikey={api_key}"
    )
    
    response = requests.get(url).json()

    if "values" not in response:
        raise Exception("Error fetching data: " + str(response))

    df = pd.DataFrame([{
        "timestamp": pd.to_datetime(entry["datetime"]),
        "open": float(entry["open"]),
        "high": float(entry["high"]),
        "low": float(entry["low"]),
        "close": float(entry["close"]),
        "volume": float(entry["volume"]),
    } for entry in response["values"]])

    df = df.sort_values("timestamp").reset_index(drop=True)
    return df























#####################################################################################################3









ticker = best
df_15min = get_live_stock_data(ticker, interval='5min')
df_15min.to_csv("df_15min.csv", index=False)

# Split into 4/5 (test) and 1/5 (train)
split_index = int(len(df_15min) * 4 / 5)  # 4000 for 5000 rows

test_df_15min = df_15min.iloc[:split_index].copy().reset_index(drop=True)
train_df_15min = df_15min.iloc[split_index:].copy().reset_index(drop=True)

# Optionally save them
test_df_15min.to_csv("test_df_15min.csv", index=False)
train_df_15min.to_csv("train_df_15min.csv", index=False)

def markov_adaptation(forecast_pct, real_pct):
        def classify(x):
            if x > 0.0005: return "UP"
            elif x < -0.0005: return "DOWN"
            else: return "FLAT"

        from collections import defaultdict

        def build_chain(states):
            chain = defaultdict(lambda: defaultdict(int))
            for (s1, s2) in zip(states[:-1], states[1:]):
                chain[s1][s2] += 1
            for s1 in chain:
                total = sum(chain[s1].values())
                for s2 in chain[s1]:
                    chain[s1][s2] /= total
            return chain

        def predict_seq(chain, start_state, steps):
            result = [start_state]
            current = start_state
            for _ in range(steps - 1):
                next_states = list(chain[current].keys())
                if not next_states:
                    break
                probs = list(chain[current].values())
                current = np.random.choice(next_states, p=probs)
                result.append(current)
            return result

        real_states = [classify(p) for p in real_pct]
        chain = build_chain(real_states)
        forecast_states = [classify(p) for p in forecast_pct]
        adapted_states = predict_seq(chain, forecast_states[-1], len(forecast_states))
        mapping = {"UP": 0.001, "DOWN": -0.001, "FLAT": 0.0}
        return pd.Series([mapping[s] for s in adapted_states]).cumsum()


import datetime
from datetime import datetime as datetime_o
import traceback

if __name__ == "__main__":
    print(">>> Script started")
    future = None
    model_b_day = datetime_o.now()
    training_time = 20 * 60
    pos = 0
    bot = IBTradingBot()
    ticker = ticker
    interval_range = 5
    forecasting_horizon = 5
    static_covariates = None
    this_is_a_test = True
    both_price = None
    first_pred = False
    sleep_time = 2.5 * 60
    profit_constant = 0.0062
    results_df = pd.DataFrame(columns=["timestamp", "Buy_Signal", "close"])
    print(f'Model used: {model}')

    clientId = 1
    connected = False

    while not connected:
        try:
            print(">>> Trying to connect to IB")
            bot.connect(clientId=clientId)
            connected = True
            print(">>> Connected to IB")
        except RuntimeError as e:
            if "nextValidId" in str(e):
                print(f"[WARN] nextValidId not received for clientId={clientId}, retrying...")
                bot.disconnect()
                time.sleep(2)
                clientId += 1
            else:
                raise

    try:
        while True:
            print(">>> Starting main loop iteration")

            if True: #datetime_o.now() - model_b_day >= timedelta(minutes=training_time / 60):
                if future is None or future.done() or future.cancelled():
                    print(">>> Model training time condition met")
                    if 'df_15min' not in globals() or df_15min is None:
                        df_15min = get_live_stock_data(ticker, interval='5min')

                        df_15min = df_15min.reset_index(drop=True)

                        if df_15min['timestamp'].iloc[-1] < df_15min['timestamp'].iloc[0]:
                            print(">>> Reversing df_15min")
                            df_15min = df_15min.iloc[::-1].reset_index(drop=True)


                    executor = ThreadPoolExecutor(max_workers=1)
                    future = executor.submit(background_training)

            if future and future.done():
                print(">>> Future training completed")
                model, training_time = future.result()
                model_b_day = datetime_o.now()
                print(f"[✓] Training completed: model={model}, time={training_time:.2f}s")

            if (is_market_open() or this_is_a_test) and first_pred:
                print(">>> Market is open and it's the first prediction")
                df_1min = get_live_stock_data(ticker)
                hourly_df = get_hourly_stock_data(ticker)
                df_15min = get_live_stock_data(ticker, interval='5min')

                df_1min = df_1min.reset_index(drop=True)
                df_15min = df_15min.reset_index(drop=True)

                if df_1min['timestamp'].iloc[-1] < df_1min['timestamp'].iloc[0]:
                    print(">>> Reversing df_1min")
                    df_1min = df_1min.iloc[::-1].reset_index(drop=True)

                if df_15min['timestamp'].iloc[-1] < df_15min['timestamp'].iloc[0]:
                    print(">>> Reversing df_15min")
                    df_15min = df_15min.iloc[::-1].reset_index(drop=True)

                if hourly_df['timestamp'].iloc[-1] < hourly_df['timestamp'].iloc[0]:
                    print(">>> Reversing hourly_df")
                    hourly_df = hourly_df.iloc[::-1].reset_index(drop=True)

                print(df_15min.tail(2))
                print(df_1min.tail(2))
                print(hourly_df.tail(1))
                print(ticker)

                if USE_STATIC_COV:
                    print(">>> Using static covariates")
                    signal, long_signal, long_highest_forecast = buy_signal(
                        n_df=df_15min, model=model, min_df=df_1min,
                        static_covariates=static_covariates,
                        first_pred=first_pred, n=5,
                        forecasting_horizon=5, long_model=long_model,
                        long_n_df=hourly_df
                    )
                if USE_STATIC_COV == False:
                    print(">>> Not using Static Covariates")
                    signal, long_signal, long_highest_forecast = buy_signal(
                        n_df=df_15min, model=model, min_df=df_1min,
                        first_pred=first_pred, n=5,
                        forecasting_horizon=5, long_model=long_model,
                        long_n_df=hourly_df
                    )

                if (signal > profit_constant) and (long_signal > 0.012) and pos == 0:
                    print(">>> Buy signal detected")
                    both_price = bot.buy(ticker)
                    pos = 1
                    open_signal = True

                if both_price is not None:
                    print(">>> Calculating exit potential")
                    exit_potential = percent_diff = ((long_highest_forecast - both_price) / both_price) * 100

                elif both_price is not None and (signal < (profit_constant - 0.004)) and pos == 1:
                    print(">>> Sell condition check")
                    if exit_potential < 0.02:
                        print(">>> Sell signal detected")
                        bot.close_buy(ticker)
                        pos = 0
                        open_signal = False

                elif pos == 0:
                    print(">>> No position open")
                    open_signal = False

                print(">>> Saving signal to JSON")
                save_signal_to_json(open_signal)

                print(">>> Logging results to DataFrame")
                results_df = pd.concat([
                    results_df,
                    pd.DataFrame({
                        "timestamp": [df_1min['timestamp'].iloc[-1]],
                        "Buy_Signal": [open_signal],
                        "close": [df_1min['close'].iloc[-1]]
                    })
                ], ignore_index=True)

                if this_is_a_test:
                    print(">>> Test mode: breaking loop")
                    break
                time.sleep(sleep_time)
                first_pred = False

            elif (is_market_open() or this_is_a_test) and not first_pred:
                print(">>> Market is open, not first prediction")
                df_1min = get_live_stock_data(ticker)
                hourly_df = get_hourly_stock_data(ticker)
                df_15min = get_live_stock_data(ticker, interval='5min')

                df_1min = df_1min.reset_index(drop=True)
                df_15min = df_15min.reset_index(drop=True)

                if df_1min['timestamp'].iloc[-1] < df_1min['timestamp'].iloc[0]:
                    print(">>> Reversing df_1min")
                    df_1min = df_1min.iloc[::-1].reset_index(drop=True)

                if df_15min['timestamp'].iloc[-1] < df_15min['timestamp'].iloc[0]:
                    print(">>> Reversing df_15min")
                    df_15min = df_15min.iloc[::-1].reset_index(drop=True)

                if hourly_df['timestamp'].iloc[-1] < hourly_df['timestamp'].iloc[0]:
                    print(">>> Reversing hourly_df")
                    hourly_df = hourly_df.iloc[::-1].reset_index(drop=True)

                print(df_15min.tail(2))
                print(df_1min.tail(2))
                print(hourly_df.tail(1))
                print(ticker)

                if USE_STATIC_COV:
                    print(">>> Using static covariates")
                    signal, long_signal, long_highest_forecast = buy_signal(
                        n_df=df_15min, model=model, min_df=df_1min,
                        static_covariates=static_covariates,
                        first_pred=first_pred, n=5,
                        forecasting_horizon=5, long_model=long_model,
                        long_n_df=hourly_df
                    )
                if USE_STATIC_COV == False:
                    print(">>> Not using Static Covariates")
                    signal, long_signal, long_highest_forecast = buy_signal(
                        n_df=df_15min, model=model, min_df=df_1min,
                        first_pred=first_pred, n=5,
                        forecasting_horizon=5, long_model=long_model,
                        long_n_df=hourly_df
                    )

                if (signal > profit_constant) and (long_signal > 0.012) and pos == 0:
                    print(">>> Buy signal detected")
                    both_price = bot.buy(ticker)
                    pos = 1
                    open_signal = True

                if both_price is not None:
                    print(">>> Calculating exit potential")
                    exit_potential = percent_diff = ((long_highest_forecast - both_price) / both_price) * 100

                elif both_price is not None and (signal < (profit_constant - 0.004)) and pos == 1:
                    print(">>> Sell condition check")
                    if exit_potential < 0.02:
                        print(">>> Sell signal detected")
                        bot.close_buy(ticker)
                        pos = 0
                        open_signal = False

                elif pos == 0:
                    print(">>> No position open")
                    open_signal = False

                print(">>> Saving signal to JSON")
                save_signal_to_json(open_signal)

                print(">>> Logging results to DataFrame")
                results_df = pd.concat([
                    results_df,
                    pd.DataFrame({
                        "timestamp": [df_1min['timestamp'].iloc[-1]],
                        "Buy_Signal": [open_signal],
                        "close": [df_1min['close'].iloc[-1]]
                    })
                ], ignore_index=True)

                first_pred = False

                if this_is_a_test:
                    print(">>> Test mode: breaking loop")
                    break
                time.sleep(sleep_time)
                today_str = datetime_o.now().strftime('%Y-%m-%d')

    except Exception as e:
        print(f"An error occurred: {e}")
        print("• Full traceback:")
        traceback.print_exc()
        today_str = datetime_o.now().strftime('%Y-%m-%d')
        bot.disconnect()
