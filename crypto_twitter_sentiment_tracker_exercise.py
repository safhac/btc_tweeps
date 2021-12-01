import asyncio
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, timezone
from typing import List, TypeVar
from urllib.request import urlopen
import tweepy  # using version 4.1.0

# UTC
utc_now = lambda: datetime.utcnow().replace(tzinfo=timezone.utc)

URL = "https://financialmodelingprep.com/api/v3/quote/BTCUSD?apikey=9c33655ac70d040280297ef04cf3ceff"

# Twitter OAuth Authentication
CONSUMER_KEY = "dqyaBG6BbC1gETauyEDyoyaib"
CONSUMER_SECRET = "pKvBnWNT7Wxr7Z3WwQzhtJ1BlF1cKNw7LEN0597jYsSEE1cCTu"

ACCESS_TOKEN = "1269644061079674888-NzGrf0MAEVl6fGDSTtpUTYJMNBezvb"
ACCESS_TOKEN_SECRET = "ubqTldQLx7atDcXUwUlWJ8lLqx1wWkrkCKud97n6PswpN"

Tweet = TypeVar("Tweet")


def save_task_results(price: float, tweets: List[Tweet]):
    # calculate
    # sentiment = like + 2 * retweet
    # sum all sentiments
    # save record format:
    # time_stamp, bitcoin_price, last_min_tweets, batch_sentiment_score

    sentiments = []
    # filter tweets from the last minute here!
    last_minute = utc_now() - timedelta(minutes=1)
    last_min_tweets = list(filter(lambda t: t.created_at > last_minute, tweets))
    for tweet in last_min_tweets:
        retweets = tweet.retweet_count
        likes = tweet.favorite_count
        sentiments.append(likes + retweets * 2)

    last_min_sentiment = sum(sentiments) / len(tweets)
    tweets_as_json = list(map(lambda t: t._json, last_min_tweets))
    t_result = TaskResult(utc_now(), price, json.dumps(tweets_as_json), last_min_sentiment)
    with open('db.json', 'w') as db:
        db.writelines(json.dumps(asdict(t_result)))



@dataclass
class TaskResult:
    """
    keep task results tidy
    """
    time_stamp: datetime
    bitcoin_price: float
    last_min_tweets: List[Tweet]
    batch_sentiment_score: float


class MyTweepyApi:
    def __init__(self,
                 api: tweepy.API,
                 query: str,
                 until: datetime,
                 every: int) -> None:
        """
        class representing the task
        :param api: the api used
        :param query: the query for the api
        :param delta: running time delta
        :param every: scheduled running period
        """
        self.api = api
        self.query = query
        self.every = every
        self.until = until
        self.task = asyncio.create_task(self.periodic())

    async def start(self):
        await self.task

    async def stop(self):
        self.task.cancel()

    async def get_json_parsed_data(self, url: str) -> str:
        response = urlopen(url)
        data = response.read().decode("utf-8")
        return json.loads(data)

    async def get_btc_price(self):
        parsed_data = (await self.get_json_parsed_data(URL))[0]
        return parsed_data["price"]

    async def get_btc_tweets(self):

        return self.api.search_tweets(
            q=self.query,
            result_type="recent",
            count=100,
            tweet_mode='extended'
        )

    async def periodic(self) -> None:
        while utc_now() < self.until:
            price, results = await asyncio.gather(
                self.get_btc_price(),
                self.get_btc_tweets()
            )
            # save results
            save_task_results(price, results)
            await asyncio.sleep(self.every)

        else:
            print('completed')
            await self.stop()


async def main(api: tweepy.API) -> None:
    print("Welcome to crypto twitter sentiment tracker")

    until = utc_now() + timedelta(hours=2)
    every = 60  # in seconds
    query = "$BTC" + " -filter:retweets"

    tweepy_api = MyTweepyApi(api, query, until, every)
    try:
        await tweepy_api.start()

    except asyncio.CancelledError as e:
        print(e, e.args)


if __name__ == "__main__":
    # Configure tweepy

    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)

    asyncio.run(main(api))
