from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

urls = ['/', '/rules', '/rooms', '/messages', '/1/1']


class MyAppTestCase(AioHTTPTestCase):
    @unittest_run_loop
    async def test_chat(self):
        for url in urls:
            response = await self.client.request('GET', url)
            assert response.status == 200