import json
from urllib.request import urlopen
import tweepy  # using version 4.1.0


def get_jsonparsed_data(url):
    response = urlopen(url)
    data = response.read().decode("utf-8")
    return json.loads(data)


if __name__ == "__main__":

    print("Welcome to crypto twitter sentiment tracker")

    url = "https://financialmodelingprep.com/api/v3/quote/BTCUSD?apikey=9c33655ac70d040280297ef04cf3ceff"
    parsed_data = get_jsonparsed_data(url)[0]
    price = parsed_data["price"]

    print("bitcoin price: " + str(price))

    # Twitter OAuth Authentication
    consumer_key = "dqyaBG6BbC1gETauyEDyoyaib"
    consumer_secret = "pKvBnWNT7Wxr7Z3WwQzhtJ1BlF1cKNw7LEN0597jYsSEE1cCTu"

    access_token = "1269644061079674888-NzGrf0MAEVl6fGDSTtpUTYJMNBezvb"
    access_token_secret = "ubqTldQLx7atDcXUwUlWJ8lLqx1wWkrkCKud97n6PswpN"

    # Configure tweepy
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    twitter_api = tweepy.API(auth)

    query_string = "$BTC" + " -filter:retweets"

    tweets = twitter_api.search_tweets(q=query_string, result_type="recent", count=100, tweet_mode='extended')
    print(tweets[0])
