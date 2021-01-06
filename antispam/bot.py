import aiohttp
import collections

# ban-users list
store_bot = collections.Counter()


async def antispam_bot():

    async with aiohttp.ClientSession() as session:
        async with session.get('http://localhost:8080/') as resp:
            if resp.status == 200:
                print('Bot is running')
            else:
                raise Exception('Bot is NOT running')

            chat_content = await resp.read()
            print(chat_content)
            print(await resp.text())