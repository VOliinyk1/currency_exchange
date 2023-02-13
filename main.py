import json
import platform
import asyncio
import logging
from abc import abstractmethod
from datetime import datetime, timedelta
import argparse
import aiohttp


parser = argparse.ArgumentParser()

parser.add_argument('days')

args = parser.parse_args()


class СurrencyRate():
    def __init__(self, days):
        self.url = 'https://api.privatbank.ua/p24api/exchange_rates?date=01.12.2014'
        self.days = days if days <= 10 else 10

    @abstractmethod
    async def get_exchange(self):
        pass


    @abstractmethod
    def formated_urls(self, day):
        pass

    @abstractmethod
    def formated_json(self, json: json):
        pass

class USD_EURCurrencyRate(СurrencyRate):
    def formated_urls(self):
        urls = []
        for day in range(self.days):
            date = datetime.today() - timedelta(days=day)
            date = date.strftime("%d.%m.%Y")
            urls.append(self.url[:-10]+str(date))
        
        return urls

    def formated_json(self, json: json):
        date = json['date']
        exchange_rates = json['exchangeRate']
        USD = list(filter(lambda curr: 'USD' in curr.values(), exchange_rates))
        EUR = list(filter(lambda curr: 'EUR' in curr.values(), exchange_rates))
        
        json = {date: {'USD': {'sale': USD[0]['saleRate'],
                                'purchase': USD[0]['purchaseRate']}},
                        'EUR': {'sale': EUR[0]['saleRate'],
                                'purchase': EUR[0]['purchaseRate']}}
        return json
        
    async def get_exchange(self):
        async with aiohttp.ClientSession() as session:
            for url in self.formated_urls():
                logging.info(f'Starting: {url}')
                try:
                    async with session.get(url) as response:
                        if response.status == 200:
                            json = await response.json()
                            print(self.formated_json(json))
                        else:
                            logging.error(f'Error status {response.status} for {url}')
                except aiohttp.ClientConnectionError as e:
                    logging.error(f'Connection error {url} : {e}')

if __name__ == "__main__":
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        usd_rate = USD_EURCurrencyRate(days=int(args.days))
        run = asyncio.run(usd_rate.get_exchange())
        