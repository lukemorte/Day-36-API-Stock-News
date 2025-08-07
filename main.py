import requests
from stock_data import stock_data
from news_data import news_data
import smtplib
from email.message import EmailMessage

import os
from dotenv import load_dotenv
import sys


load_dotenv()

STOCK_NAME = "TSLA"
COMPANY_NAME = "Tesla Inc"

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

STOCK_API_KEY = "VAOD2LDJNEYUQPCZ"
NEWS_API_KEY = "2f8f5570b3f44a4996000599135a4efb"

PERCENT_TRESHOLD = 2

my_email = os.getenv("SMTP_USERNAME")
my_password = os.getenv("SMTP_PASSWORD")
smtpserver = os.getenv("SMTP_SERVER")

# API CALL

stock_parameters = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK_NAME,
    "apikey": STOCK_API_KEY,
}

# response = requests.get(STOCK_ENDPOINT, stock_parameters)
# response.raise_for_status()

# stock_data = response.json()  # odkpomentovat, aby se data načítala z AP

data = stock_data["Time Series (Daily)"]
yesterday_date = list(data.keys())[1]

data_values = list([values for keys, values in data.items()])



# data[0] = yesterday, data[1] = day before
data = [data_values[0], data_values[1]]

for day in data:
    day["close"] = day.pop("4. close")  # přejmenuj 4. close na close
    day["close"] = float(day["close"])


diff = data[0]["close"] - data[1]["close"]
percent_change = (diff / data[1]["close"]) * 100
print(f"change: {percent_change:.2f}%")

if percent_change > PERCENT_TRESHOLD:
    print("GET NEWS.")


# NEWS API CALL

news_parameters = {
    "q": COMPANY_NAME,
    "from": yesterday_date,
    "sortby": "popularity",
    "apikey": NEWS_API_KEY
}

# response = requests.get(NEWS_ENDPOINT, news_parameters)
# response.raise_for_status()
# news_data = response.json()

articles = news_data["articles"][:3]
if percent_change > 0:
    sign = "🔺"
else:
    sign = "🔻"

final_articles = [f"{STOCK_NAME}: {sign}{percent_change:.2f}\nHeadline: {n["title"]}\nBrief: {n["description"]}" for n in articles]


# email

with smtplib.SMTP(smtpserver) as connection:
    connection.starttls()
    connection.login(user=my_email, password=my_password)

    msg = EmailMessage()
    msg.set_content("\n\n".join(final_articles))
    msg["Subject"] = "Stock News"
    msg["From"] = my_email
    msg["To"] = "luke_py_test@yahoo.com"

    connection.send_message(msg)