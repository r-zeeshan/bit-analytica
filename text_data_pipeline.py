from transformers import BertTokenizer, BertForSequenceClassification
from data_scrapper import fetch_24hrs
from text_utils import clean_text, get_sentiment, aggregate_sentiment
from config import IMPACT_WEIGHTS
import nltk
import pandas as pd
from datetime import datetime, timedelta


class TextDataPipeline:
    """
    A class that represents a text data pipeline for sentiment analysis.

    Attributes:
        tokenizer (BertTokenizer): The tokenizer used for tokenizing the text.
        model (BertForSequenceClassification): The pre-trained BERT model for sentiment classification.

    Methods:
        getSentimentScoreForPast24Hours: Fetches data, cleans the text, and calculates sentiment scores for the past 24 hours.
        get_label_definitions: Returns the label definitions for sentiment scores.
    """

    def __init__(self, llm):
        """
        Initializes a TextDataPipeline object.

        Args:
            llm (str): The pre-trained language model to be used for tokenization and sentiment classification.
        """
        nltk.download('punkt')
        nltk.download('stopwords')
        nltk.download('wordnet')
        self.tokenizer = BertTokenizer.from_pretrained(llm)
        self.model = BertForSequenceClassification.from_pretrained(llm)

    def getSentimentScoreForPast24Hours(self):
        """
        Fetches data, cleans the text, and calculates sentiment scores for the past 24 hours.

        Returns:
            pandas.DataFrame: A DataFrame containing the aggregated sentiment scores for the past 24 hours.
        """
        data = fetch_24hrs() ## Step 1: Fetch the Data
        data['content'] = data['content'].apply(clean_text) ## Step 2: Clean the text (see method documentation for more details)
        data['sentiment'] = data['content'].apply(lambda x: get_sentiment(x, self.tokenizer, self.model)) ## Step 3: Get sentiment scores
        data = aggregate_sentiment(data, IMPACT_WEIGHTS) ## Step 4: Aggregate sentiment scores for the past 24hrs
        return data
    

    def updateSentimentScores(self, csv_path='data/sentiment_scores.csv'):
        """
        Reads the CSV, fetches and processes new data, and appends it to the CSV.

        Args:
            csv_path (str): The path to the CSV file. Defaults to 'data/sentiment_scores.csv'.
        """
        ### Step 1: Read the CSV and get the last Date
        df = pd.read_csv(csv_path, parse_dates=['Date'], index_col='Date')
        latest_date = df.index.max()

        ### Step 2: Calculate the start and end date for fetching new data
        start_date = latest_date + timedelta(days=1)
        end_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(seconds=1)

        ### Step 3: Fetch and preprocess data from start_date to end_date
        while start_date <= end_date:
            day_end = start_date + timedelta(days=1) - timedelta(seconds=1)
            data = fetch_24hrs(start=start_date, end=day_end)
            data['content'] = data['content'].apply(clean_text)
            data['sentiment'] = data['content'].apply(lambda x: get_sentiment(x, self.tokenizer, self.model))
            daily_data_aggregated = aggregate_sentiment(data, IMPACT_WEIGHTS)

            df = df.append(daily_data_aggregated, ignore_index=False)

            start_date = start_date + timedelta(days=1)


        ### Step 4: Saving the updated data
        df.to_csv(csv_path)

    def getLabelDefinitions(self):
        """
        Returns the label definitions for sentiment scores.

        Returns:
            dict: A dictionary mapping sentiment scores to their corresponding labels.
        """
        return {
            0 : 'Neutral',
            1 : 'Positive',
            2 : 'Negative'
        }
        