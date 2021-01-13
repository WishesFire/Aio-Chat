import aiohttp
import asyncio
from lxml import etree
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_HOST
from models.database import BanUsers
import lxml.html

# ban-users list
# 1 warning = pass
# 2 warning = ban 1 hour (count > 5)
FIRST_BAN = '1 hour'
# 3 warning = ban 24 hour (count > 6)
SECOND_BAN = '24 hour'
# 4 warning = ban full (count > 8)
FULL_BAN = 'gg'

# Rules: 1. (number in row > 5) == warning
#        2. (many words not in one time > 15) == warning
#       image, audio, text

db = AsyncIOMotorClient(MONGO_HOST)
main_site = 'http://localhost:8080/'
store_bot = {}
temp_message = []
last_message_count = ''


async def antispam_bot():
    print('Launching AntiSpam Bot')
    async with aiohttp.ClientSession() as session:
        while True:
            global last_message_count
            async with session.get(main_site) as resp:
                if resp.status == 200:
                    print('Bot is running')
                else:
                    raise Exception('Bot is NOT running')

                chat_content = await resp.text()
                tasks = []
                thread = asyncio.Semaphore(20)
                tree = lxml.html.document_fromstring(chat_content)
                count_div = str(tree.xpath('count(//*[@id="mess_form"]/div)'))

                if count_div == last_message_count:
                    pass
                else:
                    if last_message_count == '':
                        last_message_count = count_div
                        await give_task(count_div, thread, tree, tasks)
                    else:
                        await give_task(count_div, thread, tree, tasks, last_message_count)

            await asyncio.sleep(60)


async def give_task(count_div, thread, tree, tasks, last_message=None):
    if last_message is None:
        for count in range(int(count_div)):
            task = asyncio.ensure_future(distribution_task(count, thread, tree))
            tasks.append(task)
        await asyncio.gather(*tasks)
    else:
        for count in range(int(last_message), int(count_div)):
            task = asyncio.ensure_future(distribution_task(count, thread, tree))
            tasks.append(task)
        await asyncio.gather(*tasks)


async def distribution_task(count, thread, tree):
    try:
        async with thread:
            new_elem = await get_one(count, tree)

            if new_elem in store_bot:
                store_bot[new_elem] += 1
                if new_elem[1] == 'text' and len(new_elem[2]) > 25 and new_elem in temp_message:
                    if store_bot[new_elem] == 5:
                        await BanUsers.add_one(db=db, username=new_elem[0], status=FIRST_BAN)
                    elif store_bot[new_elem] == 6:
                        await BanUsers.add_one(db=db, username=new_elem[0], status=SECOND_BAN)
                    elif store_bot[new_elem] == 8:
                        await BanUsers.add_one(db=db, username=new_elem[0], status=FULL_BAN)

                elif new_elem[1] == 'image' and new_elem in temp_message:
                    if store_bot[new_elem] == 8:
                        await BanUsers.add_one(db=db, username=new_elem[0], status=FIRST_BAN)
                    elif store_bot[new_elem] == 9:
                        await BanUsers.add_one(db=db, username=new_elem[0], status=SECOND_BAN)
                    elif store_bot[new_elem] == 10:
                        await BanUsers.add_one(db=db, username=new_elem[0], status=FULL_BAN)

                await temp_add(new_elem)

            else:
                store_bot[new_elem] = 1
                await temp_add(new_elem)

    except Exception as e:
        print(e)


async def temp_add(new_elem):
    if len(temp_message) == 12:
        temp_message.pop()
        temp_message.append(new_elem)


async def get_one(count, tree):
    async def check(xpath):
        item = tree.xpath(xpath)
        if item:
            return item
        else:
            return None

    username = await check(f'//*[@id="mess_form"]/div[{count}]/p[1]/text()')
    text = await check(f'//*[@id="mess_form"]/div[{count}]/p[@class="hidden-text"]/text()')
    if text is None:
        image = await check(f'//*[@id="mess_form"]/div[{count}]/img[@class="size-photo"]/@src')
        if image is None:
            audio = await check('//*[@id="mess_form"]/div[59]/audio[@class="audio-mess"]')
            return (username, 'audio', audio)
        else:
            return (username, 'image', image)
    else:
        return (username, 'text', text)


def main():
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(antispam_bot())
    loop.run_until_complete(future)
    print('OVER WTF')


if __name__ == '__main__':
    main()