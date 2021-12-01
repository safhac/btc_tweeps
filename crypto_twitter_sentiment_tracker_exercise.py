import asyncio
import json
from urllib.request import urlopen
import tweepy  # using version 4.1.0

URL = "https://financialmodelingprep.com/api/v3/quote/BTCUSD?apikey=9c33655ac70d040280297ef04cf3ceff"
# Twitter OAuth Authentication
CONSUMER_KEY = "dqyaBG6BbC1gETauyEDyoyaib"
CONSUMER_SECRET = "pKvBnWNT7Wxr7Z3WwQzhtJ1BlF1cKNw7LEN0597jYsSEE1cCTu"

ACCESS_TOKEN = "1269644061079674888-NzGrf0MAEVl6fGDSTtpUTYJMNBezvb"
ACCESS_TOKEN_SECRET = "ubqTldQLx7atDcXUwUlWJ8lLqx1wWkrkCKud97n6PswpN"

QUERY_STRING = "$BTC" + " -filter:retweets"


def get_json_parsed_data(url: str) -> str:
    response = urlopen(url)
    data = response.read().decode("utf-8")
    return json.loads(data)



async def main():
    print("Welcome to crypto twitter sentiment tracker")

    parsed_data = get_json_parsed_data(URL)[0]
    price = parsed_data["price"]

    print("bitcoin price: " + str(price))

    # Configure tweepy
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    twitter_api = tweepy.API(auth)

    tweets = twitter_api.search_tweets(q=QUERY_STRING, result_type="recent", count=100, tweet_mode='extended')
    print(tweets[0])


if __name__ == "__main__":
    asyncio.run(main())



