from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop


@unittest_run_loop
async def test_chat(self):
    response = await self.client.request('GET', '/')
    assert response.status == 200