import asyncio
import json
from datetime import datetime, timedelta
from urllib.request import urlopen
import tweepy  # using version 4.1.0

# UTC
utc_now = lambda: datetime.utcnow()
# YYYY - MM - DDTHH: mm:ssZ
tweepy_strf = "%Y-%m-%d%H %m:%s"

URL = "https://financialmodelingprep.com/api/v3/quote/BTCUSD?apikey=9c33655ac70d040280297ef04cf3ceff"

# Twitter OAuth Authentication
CONSUMER_KEY = "dqyaBG6BbC1gETauyEDyoyaib"
CONSUMER_SECRET = "pKvBnWNT7Wxr7Z3WwQzhtJ1BlF1cKNw7LEN0597jYsSEE1cCTu"

ACCESS_TOKEN = "1269644061079674888-NzGrf0MAEVl6fGDSTtpUTYJMNBezvb"
ACCESS_TOKEN_SECRET = "ubqTldQLx7atDcXUwUlWJ8lLqx1wWkrkCKud97n6PswpN"


def save_task_results(results: str):
    with open('task_results', 'w') as file:
        file.writelines(results)


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

        start = utc_now() - timedelta(minutes=1)
        end = utc_now()
        return self.api.search_tweets(
            q=self.query,
            start_time=start.strftime(tweepy_strf),
            end_time=end.strftime(tweepy_strf),
            count=100,
            tweet_mode='extended'
        )

    async def periodic(self) -> None:
        while utc_now() < self.until:
            results = await asyncio.gather(
                self.get_btc_price(),
                self.get_btc_tweets()
            )
            # save results
            save_task_results(results)
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
