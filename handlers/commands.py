import datetime
from aiohttp import ClientSession


async def time_now():
    return datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")


async def curs_now():
    string_curs = ''
    async with ClientSession() as session:
        async with session.get('https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5') as response:
            assert response.status == 200
            for currency in await response.json():
                string_curs += str(currency)[1:-1] + '\n'

    return string_curs