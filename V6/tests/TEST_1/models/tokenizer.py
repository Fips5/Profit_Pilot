import pandas as pd

from tensorflow.keras.preprocessing.text import  Tokenizer

def tokenizer_return():
    csv_path = r'C:\Users\David\Documents\ProfitPilot\V6\tests\TEST_1\models\model-1\IMDB_Dataset.csv'
    df = pd.read_csv(csv_path)
    token = Tokenizer()
    token.fit_on_texts(df['review'])
    return token