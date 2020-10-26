import datetime


async def time_now():
    return datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")