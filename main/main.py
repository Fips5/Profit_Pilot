from market_data_analysis.stocks_lists import get_top_stocks
from news_fetching.yf_news_extraction import get_latest_news_list, extract_article_text
from processing_text.test_processing import input_processing
from tokenizer import tokenizer_return

from tensorflow.keras.models import load_model
import pandas as pd
from statistics import mean

tickers_list = get_top_stocks('main')

def calculate_average(numbers):
    if not numbers: 
        return 0
    return sum(numbers) / len(numbers)

def convert_score(score):
    if isinstance(score, list) and isinstance(score[0], list):
        return float(score[0][0])
    else:
        return float(score)
    
news_model_path = r'models\news\model-1\model-1.h5'
news_lstm_model = load_model(news_model_path)

tokenizer = tokenizer_return()

scores_col = []
for ticker in tickers_list:
    ticker_score_list = []
    ticker_articles_links_list = list(get_latest_news_list(ticker) or [])  
    if ticker_articles_links_list:  # Only process if not empty
        for link in ticker_articles_links_list:
            ticker_articles_text = extract_article_text(link)
            if ticker_articles_text is not None:
                processed_text = input_processing(ticker_articles_text, tokenizer, maxlen=100)
                prediction = news_lstm_model.predict(processed_text)
                ticker_score_list.append(prediction)
    if ticker_score_list is not None:
        mean_ticker_score = calculate_average(ticker_score_list)
        scores_col.append(mean_ticker_score)
    if ticker_score_list is None:
        scores_col.append(0)


tickers_news_df = pd.DataFrame({
    'Ticker': tickers_list,
    'Score': scores_col
})
    
