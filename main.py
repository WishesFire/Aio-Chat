from aiohttp import web
from handlers.base import index

async def main():
    app = web.Application()
    app.add_routes([web.get('/'), index])
    web.run_app(app)


if __name__ == '__main__':
    main()