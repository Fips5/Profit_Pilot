import numpy as np
from tensorflow.keras.preprocessing.sequence import pad_sequences
import re
import nltk
from nltk.corpus import stopwords


def remove_tags(text):
  TAG_RE = re.compile(r'<[*>]+>')
  #removes html tags and replaces anything between <> with " "
  return TAG_RE.sub('', text)

def preprocess_text(sen):
    nltk.download('stopwords')
    # Convert to lowercase
    sentence = sen.lower()

    # Remove HTML tags if any
    sentence = remove_tags(sentence)

    # Remove punctuation and numbers
    sentence = re.sub('[^a-zA-Z]', ' ', sentence)

    # Remove single characters (like 'a', 'b', 'c', etc.) surrounded by spaces
    sentence = re.sub(r"\s+[a-zA-Z]\s+", ' ', sentence)

    # Remove multiple spaces with a single space
    sentence = re.sub(r'\s+', ' ', sentence)

    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    sentence = ' '.join([word for word in sentence.split() if word not in stop_words])

    return sentence

def input_processing(text,tokenizer, maxlen=128):
    """
    Process a single text input for prediction.

    Args:
    - text (str): The input text to be processed.
    - tokenizer (Tokenizer): The tokenizer fitted on the training data.
    - maxlen (int): The maximum length for padding sequences (default is 128).

    Returns:
    - numpy.array: A processed and padded sequence ready for prediction.
    """
    # Preprocess the input text
    text_processed = preprocess_text(text)
    
    # Convert the processed text to a sequence of integers
    sequence = tokenizer.texts_to_sequences([text_processed])
    
    # Pad the sequence to the specified length
    sequence_padded = pad_sequences(sequence, padding='post', maxlen=maxlen, truncating='post')
    
    return sequence_padded



def process_texts(texts, tokenizer, maxlen=128):
    """
    Process and reshape a list of text inputs for model prediction.

    Args:
    - texts (list of str): The list of texts to be processed.
    - tokenizer (Tokenizer): The tokenizer fitted on the training data.
    - maxlen (int): The maximum length for padding sequences (default is 128).

    Returns:
    - numpy.array: An array of processed and padded sequences.
    """
    # Process each text in the list
    processed_texts = np.array([input_processing(text, tokenizer, maxlen) for text in texts])
    
    # Reshape the array to match the model's input shape if necessary
    processed_texts = processed_texts.reshape(processed_texts.shape[0], maxlen)
    
    return processed_texts
 