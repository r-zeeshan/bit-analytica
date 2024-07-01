import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem  import WordNetLemmatizer 
import torch
import pandas as pd


def clean_text(text):
    """
    Cleans the given text by performing the following steps:
    1. Converts the text to lowercase.
    2. Removes text in square brackets.
    3. Removes URLs.
    4. Removes mentions and hashtags.
    5. Removes special characters and numbers.
    6. Removes extra whitespace.
    7. Tokenizes the text.
    8. Lemmatizes the tokens and removes stop words.
    
    Args:
        text (str): The text to be cleaned.
        
    Returns:
        str: The cleaned text.
    """
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')

    lemmatizer = WordNetLemmatizer()

    text = text.lower()  # Lowercase
    text = re.sub(r'\[.*?\]', '', text)  # Remove text in square brackets
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)  # Remove URLs
    text = re.sub(r'\@w+|\#', '', text)  # Remove mentions and hashtags
    text = re.sub(r'[^a-zA-Z]', ' ', text)  # Remove special characters and numbers
    text = re.sub(r'\s+', ' ', text).strip()  # Remove extra whitespace
    tokens = word_tokenize(text)  # Tokenize
    tokens = [lemmatizer.lemmatize(word) for word in tokens if word not in stopwords.words('english')] # Lemmatize and remove stop words
    return ' '.join(tokens)


def tokenize_text(text, tokenizer, max_length=512):
    """
    Tokenizes the given text using the provided tokenizer.

    Args:
        text (str): The input text to be tokenized.
        tokenizer (Tokenizer): The tokenizer object to be used for tokenization.
        max_length (int, optional): The maximum length of the tokenized sequence. Defaults to 512.

    Returns:
        input_ids (Tensor): The tokenized input sequence as a tensor.
        attention_mask (Tensor): The attention mask for the tokenized sequence as a tensor.
    """
    encoding = tokenizer.encode_plus(
        text,
        add_special_tokens = True,
        max_length = max_length,
        return_token_type_ids = False,
        padding = 'max_length',
        truncation = True,
        return_attention_mask = True,
        return_tensors = 'pt'
    )

    return encoding['input_ids'], encoding['attention_mask']


def get_sentiment(text, tokenizer, model, max_length=512):
    """
    Get the sentiment of a given text using a tokenizer and a model.

    Args:
        text (str): The input text to analyze.
        tokenizer: The tokenizer object used to tokenize the text.
        model: The model used to predict the sentiment.
        max_length (int, optional): The maximum length of the input text. Defaults to 512.

    Returns:
        int: The predicted sentiment of the text.
    """
    input_ids, attention_mask = tokenize_text(text, tokenizer, max_length)

    with torch.no_grad():
        outputs = model(input_ids, attention_mask)

    logits = outputs[0]
    sentiment = torch.argmax(logits, dim=1).item()
    return sentiment


def aggregate_sentiment(df, impact_weights):
    """
    Aggregates sentiment values based on impact weights.

    Args:
        df (pandas.DataFrame): The input DataFrame containing sentiment values and categories.
        impact_weights (dict): A dictionary mapping categories to their respective impact weights.

    Returns:
        pandas.DataFrame: The aggregated DataFrame with the calculated aggregated sentiment values.

    """
    df['i_category'] = df['category'].map(impact_weights)
    df['w_sentiment'] = df['sentiment'] * df['i_category']

    aggregated_df = df.groupby('Date').apply(
        lambda x : pd.Series({
            "aggregated_sentiment" : x['w_sentiment'].sum() / x['i_category'].sum()
        })
    ).reset_index()

    return aggregated_df