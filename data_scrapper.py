# data_scrapper.py

import requests
import pandas as pd
from newspaper import Article
import time
from datetime import datetime, timedelta
import os
from config import BASE_URL, QUERIES, MODE, FORMAT



def scrape_url(url, retries=3, delay=5):
    """
    Fetches data from the given URL with retry mechanism.

    Args:
        url (str): The URL to fetch data from.
        retries (int, optional): The number of retries in case of failure. Defaults to 3.
        delay (int, optional): The delay (in seconds) between retries. Defaults to 5.

    Returns:
        requests.Response or None: The response object if successful, None otherwise.
    """
    for i in range(retries):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response
            else:
                print(f"Error fetching data (attempt {i+1}/{retries}): {response.status_code}, {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Request error (attempt {i+1}/{retries}): {e}")
        time.sleep(delay)
    return None



def fetch_data(start_date, end_date, file_index=None, base_dir=None, save=False):
    """
    Fetches news articles from the GDELT API based on the specified date range and saves the data to a CSV file.

    Args:
        start_date (str): The start date of the date range in the format 'YYYY-MM-DD'.
        end_date (str): The end date of the date range in the format 'YYYY-MM-DD'.
        file_index (int): The index of the file to be saved.

    Returns:
        None
    """

    df_all_articles = pd.DataFrame()
    start_date = start_date.strftime('%Y%m%d%H%M%S')
    end_date = end_date.strftime('%Y%m%d%H%M%S')
    for category, query in QUERIES.items():
        # Construct the full URL with parameters
        url = f"{BASE_URL}?query={query}&mode={MODE}&format={FORMAT}&startdatetime={start_date}&enddatetime={end_date}"
        
        # Make the request to the GDELT API
        response = scrape_url(url)
        
        if response:
            try:
                data = response.json()
            except requests.JSONDecodeError as e:
                print(f"JSON decode error for query '{category}': {e}")
                print("Response text:", response.text)
                continue
            
            # Extract the list of articles
            articles = data.get('articles', [])
            
            # Create a list to hold the article details
            article_data = []

            # Loop through each article to fetch the full text
            for article in articles:
                article_url = article.get('url', '')
                title = article.get('title', '')
                publish_date = article.get('seendate', '')
                
                # Attempt to scrape the article content with increased timeout
                try:
                    news_article = Article(article_url)
                    news_article.download()
                    news_article.parse()
                    content = news_article.text
                except Exception as e:
                    content = ''
                    print(f"Failed to scrape {article_url}: {e}")
                
                # Append the article details to the list
                article_data.append({
                    'category': category,
                    'publish_date': publish_date,
                    'title': title,
                    'url': article_url,
                    'content': content
                })
                                
                time.sleep(1)  # Sleep for 1 second between requests to not overload the server

            # Convert to a DataFrame for easier handling
            df_articles = pd.DataFrame(article_data)
            
            # Append to the main DataFrame
            df_all_articles = pd.concat([df_all_articles, df_articles], ignore_index=True)
        else:
            print(f"Failed to fetch data for query '{category}' after multiple attempts")

    if save:
        os.makedirs(base_dir, exist_ok=True)

        # Saving the DataFrame to a CSV file
        file_name = f'bitcoin_news_data_{file_index}.csv'
        file_path = os.path.join(base_dir, file_name)
        df_all_articles.to_csv(file_path, index=False)
        print(f"Saved data to {file_path}")

    return df_all_articles


def clean_dates(dataframe):
    """
    Cleans the dates in the given dataframe.

    Parameters:
    dataframe (pd.DataFrame): The dataframe containing the dates to be cleaned.

    Returns:
    pd.DataFrame: The dataframe with cleaned dates.
    """
    dataframe['publish_date'] = pd.to_datetime(dataframe['publish_date'], format='%Y%m%dT%H%M%SZ')
    dataframe['publish_date'] = dataframe['publish_date'].dt.strftime('%Y-%m-%d')

    dataframe.set_index('publish_date', inplace=True)
    dataframe.sort_index(inplace=True)

    return dataframe


def fetch_historical_data(start_date, file_index, base_dir, end_date=None):
    """
    Fetches historical data from a specified start date to an optional end date.

    Args:
        start_date (str): The start date in the format 'YYYY-MM-DD'.
        file_index (int): The index of the file to fetch the data into.
        base_dir (str): The base directory where the data will be saved.
        end_date (str, optional): The end date in the format 'YYYY-MM-DD'. Defaults to the current date.

    Returns:
        None
    """
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d') if end_date is not None else datetime.now()

    fetch_data(start_date=start_date, end_date=end_date, file_index=file_index, base_dir=base_dir, save=True)


def fetch_past_24hrs():
    """
    Fetches data for the past 24 hours.

    Returns:
        The data fetched for the past 24 hours.
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=1)

    dataframe = fetch_data(start_date=start_date, end_date=end_date)
    dataframe = clean_dates(dataframe)

    return dataframe


def combine_news_data(base_dir, start_date, end_date):
    """
    Combine multiple CSV files containing bitcoin news data into a single DataFrame.

    Args:
        base_dir (str): The base directory where the CSV files are located.
        start_date (str): The start date of the time range for the news data.
        end_date (str): The end date of the time range for the news data.

    Returns:
        None

    Raises:
        FileNotFoundError: If the base directory does not exist or is empty.

    """
    base_dir = base_dir

    dataframes = []

    for filename in sorted(os.listdir(base_dir)):
        if filename.startswith('bitcoin_news_data_') and filename.endswith('.csv'):
            filepath = os.path.join(base_dir, filename)
            df = pd.read_csv(filepath)
            dataframes.append(df)


    combined_df = pd.concat(dataframes, ignore_index=True)
    combined_df = clean_dates(combined_df)
    combined_df.dropna(subset='content', inplace=True)
    combined_df.to_csv('bitcoin_news_data.csv')

    print(f"All bitcoin news data saved in 'bitcoin_news_data.csv' for time range {start_date} to {end_date}.")


if __name__ == '__main__':
    choice = 1
    if choice == 1:
        start_date = '2017-01-01'
        end_date = '2017-01-15'
        fetch_historical_data(start_date=start_date, file_index=0, base_dir='test', end_date=end_date)
    else:
        data = fetch_past_24hrs()
    