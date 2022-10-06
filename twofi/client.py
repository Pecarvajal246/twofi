from multiprocessing.managers import BaseManager


def categories():
    categories = m.categories()
    return categories


def livestreams():
    livestreams = m.livestreams()
    return livestreams


def import_user_follows(user: str):
    return m.import_follows(user)


def get_live_streams(channels=None, channel_id=None, game_id=None):
    livestreams = m.get_live_streams(channels, channel_id, game_id)
    return livestreams


def get_categories(query=None):
    return m.get_categories(query)._getvalue()


def get_category_streams(category: str):
    category_streams = m.get_category_streams(category)
    return category_streams


def get_channels(channel: str):
    return m.get_channels(channel)._getvalue()


def update_db_streams(channel: str, follow: bool):
    m.update_db_streams(channel, follow)
    return


def update_db_categories(category: str, follow: bool):
    m.update_db_categories(category, follow)
    return


BaseManager.register("livestreams")
BaseManager.register("categories")
BaseManager.register("import_follows")
BaseManager.register("get_live_streams")
BaseManager.register("get_categories")
BaseManager.register("get_category_streams")
BaseManager.register("get_channels")
BaseManager.register("update_db_streams")
BaseManager.register("update_db_categories")
m = BaseManager(address=("0.0.0.0", 50000), authkey=b"abc")
m.connect()
