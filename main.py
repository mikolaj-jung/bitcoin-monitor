import requests
import datetime
import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

AV_API_KEY = os.environ.get("AV_API_KEY")
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")
TWILIO_SID = os.environ.get("TWILIO_SID")
TWILIO_API_KEY = os.environ.get("TWILIO_API_KEY")
TWILIO_NUM = os.environ.get("TWILIO_NUM")
MY_NUM = os.environ.get("MY_NUM")

today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)
day_before_yesterday = today - datetime.timedelta(days=2)

# Crypto Data
crypto_params = {
    "function": "DIGITAL_CURRENCY_DAILY",
    "symbol": "BTC",
    "market": "USD",
    "apikey": AV_API_KEY,
}

response = requests.get(url="https://www.alphavantage.co/query", params=crypto_params)

crypto_data_yesterday = float(response.json()['Time Series (Digital Currency Daily)'][str(yesterday)]['4. close'])
crypto_data_before_yesterday = float(response.json()['Time Series (Digital Currency Daily)'][str(day_before_yesterday)]['4. close'])

crypto_difference = crypto_data_yesterday - crypto_data_before_yesterday
crypto_difference_perc = round(crypto_difference / crypto_data_before_yesterday * 100, 1)

# News
news_params = {
    "qInTitle": "bitcoin",
    "apiKey": NEWS_API_KEY,
    "from": day_before_yesterday,
    "to": yesterday,
    "sortBy": "publishedAt",
}

response = requests.get(url="https://newsapi.org/v2/everything", params=news_params)

def create_message():
    news_message = ""

    if crypto_difference_perc > 0:
        news_message = f"BTC: 🔺{crypto_difference_perc}%\n\n"
    else:
        news_message = f"BTC: 🔻{crypto_difference_perc}%\n\n"

    for n in range(3):
        news_title = response.json()['articles'][n]['title']
        news_description = response.json()['articles'][n]['description']
        news_message += f"Headline: {news_title}\nBrief: {news_description}\n\n"

    return news_message

# Send SMS if difference is greater than 3%
if abs(crypto_difference_perc) > 3:
    client = Client(TWILIO_SID, TWILIO_API_KEY)

    message = client.messages.create(
        body=create_message(),
        from_=TWILIO_NUM,
        to=MY_NUM,
    )