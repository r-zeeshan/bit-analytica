### Define the base LLM for the Text Sentiment Analysis
LLM = 'yiyanghkust/finbert-tone'

### Define the base URL for the GDELT GEO 2.0 API
BASE_URL = "https://api.gdeltproject.org/api/v2/doc/doc"

### DEFINING SOME COMPLEX QUERIES REGARDING BTC NEWS OR GLOBAL EVENTS THAT MAY AFFECT BTC PRICE
QUERIES = {
    "regulatory_news": '"Bitcoin" AND ("cryptocurrency regulation" OR "crypto law" OR "bitcoin ban" OR "crypto restriction" OR "government cryptocurrency regulation") -domain:3ajlnews.com sourcelang:english',
    "legal_actions": '"Bitcoin" AND ("cryptocurrency lawsuit" OR "legal action against bitcoin" OR "bitcoin ban" OR "bitcoin court case" OR "government legal action on bitcoin") -domain:3ajlnews.com sourcelang:english',
    "market_adoption": '"Bitcoin" AND ("cryptocurrency adoption" OR "accepting bitcoin" OR "bitcoin as payment" OR "financial institution bitcoin" OR "company accepting bitcoin") -domain:3ajlnews.com sourcelang:english',
    "exchange_news": '"Bitcoin" AND ("cryptocurrency exchange" OR "crypto exchange hack" OR "exchange security breach" OR "new bitcoin exchange launch" OR "bitcoin exchange shutdown") -domain:3ajlnews.com sourcelang:english',
    "blockchain_innovations": '"Bitcoin" AND ("blockchain technology" OR "bitcoin technology upgrade" OR "bitcoin hard fork" OR "bitcoin innovation") -domain:3ajlnews.com sourcelang:english',
    "security_enhancements": '"Bitcoin" AND ("cryptocurrency security" OR "bitcoin cybersecurity" OR "bitcoin security enhancement" OR "bitcoin protection measures") -domain:3ajlnews.com sourcelang:english',
    "macro_economic_trends": '"Bitcoin" AND ("economic impact" OR "bitcoin inflation hedge" OR "bitcoin monetary policy" OR "bitcoin economic indicator") -domain:3ajlnews.com sourcelang:english',
    "market_movements": '"Bitcoin" AND ("bitcoin price movement" OR "impact of stock market on bitcoin" OR "commodities influence on bitcoin" OR "bitcoin market trend") -domain:3ajlnews.com sourcelang:english',
    "institutional_involvement": '"Bitcoin" AND ("institutional investment in bitcoin" OR "hedge fund bitcoin investment" OR "public company bitcoin investment") -domain:3ajlnews.com sourcelang:english',
    "etf_news": '"Bitcoin" AND ("bitcoin ETF approval" OR "bitcoin exchange-traded fund" OR "bitcoin investment vehicle") -domain:3ajlnews.com sourcelang:english',
    "media_coverage": '"Bitcoin" AND ("bitcoin media coverage" OR "mainstream media bitcoin news" OR "bitcoin news report") -domain:3ajlnews.com sourcelang:english',
    "social_media_trends": '"Bitcoin" AND ("bitcoin social media trend" OR "bitcoin Twitter trends" OR "celebrity bitcoin endorsement") -domain:3ajlnews.com sourcelang:english',
    "geopolitical_events": '"Bitcoin" AND ("bitcoin geopolitical impact" OR "bitcoin global event" OR "bitcoin crisis impact" OR "bitcoin as safe haven") -domain:3ajlnews.com sourcelang:english',
}


### Defining the common parameters
MODE = "ArtList"
FORMAT = "json"

IMPACT_WEIGHTS = {
    'regulatory_news': 13,
    'legal_actions': 12,
    'market_adoption': 11,
    'exchange_news': 10,
    'institutional_involvement': 9,
    'macro_economic_trends': 8,
    'geopolitical_events': 7,
    'blockchain_innovations': 6,
    'market_movements': 5,
    'etf_news': 4,
    'media_coverage': 3,
    'security_enhancements': 2,
    'social_media_trends': 1
}


### Saving the column Names
SMA7 = 'SMA_7'
SMA14 = 'SMA_14'
EMA7 = 'EMA7'
EMA14 = 'EMA14'
RSI = 'RSI'
MACD = 'MACD'
SIGNAL_LINE = 'Signal Line'
BOLLINGER_SMA = 'Bollinger_SMA'
UPPER_BAND_BB = 'Upper_Band_BB'
LOWER_BAND_BB = 'Lower_Band_BB'
ATR = 'ATR'
K = '%K'
D = '%D'
OBV = 'OBV'