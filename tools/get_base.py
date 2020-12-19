from aiohttp_session import get_session


async def get_base_needed(request):
    db = request.app['db']
    session = await get_session(request)
    return db, session