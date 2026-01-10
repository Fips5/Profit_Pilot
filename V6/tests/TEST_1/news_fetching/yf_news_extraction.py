import requests
from bs4 import BeautifulSoup
import pandas as pd

import requests
from bs4 import BeautifulSoup

def extract_article_text(url):
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

        # Extract the article content (this may need to be adjusted based on the actual page structure)
        article_body = soup.find('div', {'class': 'caas-body'})  # Adjust this if necessary
        if not article_body:
            print("Article body not found.")
            return None

        paragraphs = article_body.find_all('p')
        if not paragraphs:
            print("No paragraphs found in the article.")
            return None
        
        article_text = ' '.join(p.get_text(strip=True) for p in paragraphs)
        return article_text
    else:
        print(f"Failed to retrieve the content. Status code: {response.status_code}")
        return None


def get_latest_news_list(stock_symbol):
    url = f'https://finance.yahoo.com/quote/{stock_symbol}/'
    response = requests.get(url)

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the div containing the news articles
    news_section = soup.find('div', {'id': 'tabpanel-news'})

    # Initialize an empty list to store the news links
    news_links = []

    if  news_section != None:
    # Loop through all article sections and extract the links
        for article in news_section.find_all('a', {'class': 'subtle-link'}):
            link = article.get('href')
            #full_link = 'https://finance.yahoo.com' + link
            news_links.append(link)
        return news_links
    else:
        return None