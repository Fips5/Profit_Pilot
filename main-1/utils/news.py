import pandas as pd
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import torch
import requests
from bs4 import BeautifulSoup
from transformers import pipeline
import os
import pandas_market_calendars as mcal
from datetime import datetime
import json


def get_zacks_rank(symbol):
    """
    Retrieve the Zacks Rank for a given stock symbol from Zacks.com.

    Parameters:
        symbol (str): The stock symbol (e.g., 'AAPL').

    Returns:
        float: The Zacks Rank as a float if found, else NaN.
    """
    try:
        url = f"https://www.zacks.com/stock/quote/{symbol}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        # Fetch the webpage
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Parse the webpage
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the Zacks Rank
        rank_tag = soup.find('p', class_='rank_view')
        
        if rank_tag:
            # Extract the first character of the string and convert it to float
            rank_text = rank_tag.text.strip()
            return float(rank_text[0])  # First character as float
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
    # Yahoo Finance URL for the stock's news section
    url = f"https://finance.yahoo.com/quote/{stock_symbol}/news"

    # Define headers to mimic a browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'
    }

    # Send a GET request to fetch the raw HTML content
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the latest news articles using the specific <a> tag class
        news_items = soup.find_all('a', class_='subtle-link fin-size-small titles noUnderline yf-1xqzjha')
        
        # Extract the news headlines and URLs
        news = []
        for item in news_items:
            headline = item.get_text(strip=True)
            link = item['href']
            full_link = link
            news.append({'Headline': headline, 'URL': full_link})

        # Convert the list of dictionaries into a pandas DataFrame
        yf_links_df = pd.DataFrame(news)

        return yf_links_df
    else:
        print("Failed to retrieve the news. Status code:", response.status_code)
        return None

import pandas as pd

def get_symbols_from_excel():
    file_path = "Top_80_S&P_Companies.xlsx"
    try:
        # Read the Excel file
        df = pd.read_excel(file_path)
        
        # Extract the 'Symbol' column as a list
        symbols = df['Symbol'].tolist()
        
        return symbols
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def sentiment(symbols):
    symbols_sentiment_results = []
    #symbols = get_symbols_from_excel()
    for symbol in symbols:
        # Fetch latest news DataFrame for the symbol
        news_df = get_latest_news_df(symbol)

        if not news_df['Headline'].empty:
        # Analyze the sentiment of each headline
            symbol_sentiment_results = analyze_financial_news(list(news_df['Headline']))
        #print(f'\n - {symbol} - \n {symbol_sentiment_results}')
    
        # Initialize a sentiment score
            general_sentiment_score = 0

        # Process each sentiment result
            for result in symbol_sentiment_results:
        # Filter out results with score < 0.65
                if result['score'] >= 0.65:
                    if result['label'] == 'positive':
                        general_sentiment_score += 1
                    elif result['label'] == 'negative':
                        general_sentiment_score -= 1
                # Neutral adds 0, so no action is needed for it
    
        # Append the final sentiment score for the symbol
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

import requests
from bs4 import BeautifulSoup
import pandas as pd

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