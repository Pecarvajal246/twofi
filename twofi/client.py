from multiprocessing.managers import BaseManager


def categories():
    categories = m.api().categories()
    return categories


def livestreams():
    livestreams = m.api().livestreams()
    return livestreams


def import_user_follows(user: str):
    return m.api().import_follows(user)


def get_live_streams(channels=None, channel_id=None, game_id=None):
    livestreams = m.api().get_live_streams(channels, channel_id, game_id)
    return livestreams


def get_categories(query=None):
    return m.api().get_categories(query)


def get_category_streams(category: str):
    category_streams = m.api().get_category_streams(category)
    return category_streams


def get_channels(channel: str):
    return m.api().get_channels(channel)


def update_db_streams(channel: str, follow: bool):
    m.api().update_db_streams(channel, follow)
    return


def update_db_categories(category: str, follow: bool):
    m.api().update_db_categories(category, follow)
    return


BaseManager.register("api")
m = BaseManager(address=("0.0.0.0", 50000), authkey=b"abc")
m.connect()
