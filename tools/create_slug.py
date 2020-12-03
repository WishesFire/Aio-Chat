from slugify import slugify


async def create_slug(room_name):
    return slugify(room_name).lower()