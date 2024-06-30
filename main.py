import pandas as pd
import os


base_dir = 'news_data'

dataframes = []

for filename in sorted(os.listdir(base_dir)):
    if filename.startswith('bitcoin_news_data_') and filename.endswith('.csv'):
        filepath = os.path.join(base_dir, filename)
        df = pd.read_csv(filepath)
        dataframes.append(df)


combined_df = pd.concat(dataframes, ignore_index=True)

combined_df['publish_date'] = pd.to_datetime(combined_df['publish_date'], format='%Y%m%dT%H%M%SZ')
combined_df['publish_date'] = combined_df['publish_date'].dt.strftime('%Y-%m-%d')

combined_df.set_index('publish_date', inplace=True)
combined_df.sort_index(inplace=True)

combined_df.to_csv('bitcoin_news_data.csv')

print("All bitcoin news data saved in 'bitcoin_news_data.csv' for time range 2017-01-01 to 2024-06-29.")
