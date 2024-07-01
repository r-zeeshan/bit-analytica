from transformers import BertTokenizer, BertForSequenceClassification
from data_scrapper import fetch_past_24hrs
from text_utils import clean_text, get_sentiment, aggregate_sentiment
from config import IMPACT_WEIGHTS
import nltk


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
        data = fetch_past_24hrs() ## Step 1: Fetch the Data
        data['content'] = data['content'].apply(clean_text) ## Step 2: Clean the text (see method documentation for more details)
        data['sentiment'] = data['content'].apply(lambda x: get_sentiment(x, self.tokenizer, self.model)) ## Step 3: Get sentiment scores
        data = aggregate_sentiment(data, IMPACT_WEIGHTS) ## Step 4: Aggregate sentiment scores for the past 24hrs
        return data

    def get_label_definitions(self):
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
        