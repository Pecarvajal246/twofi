from multiprocessing.managers import BaseManager
import copy


def streams():
    return copy.deepcopy(m.streams())


def categories():
    return copy.deepcopy(m.categories())


def livestreams():
    return copy.deepcopy(m.livestreams())


def get_follows():
    return copy.deepcopy(m.follows())


def import_user_follows(user: str):
    return m.import_follows(user)


def get_live_streams(channels=None, channel_id=None, game_id=None):
    return copy.deepcopy(m.get_live_streams(channels, channel_id, game_id))


def get_categories(query=None):
    return copy.deepcopy(m.get_categories(query))


def get_category_streams(category: str):
    return copy.deepcopy(m.get_category_streams(category))


def get_channels(channel: str):
    return copy.deepcopy(m.get_channels(channel))

def update_db_streams(followed_channels: list, channel: str, insert: bool):
    m.update_db_streams(followed_channels, channel, insert)
    return

def update_db_categories(followed_categories: list):
    m.update_db_categories(followed_categories)
    return

BaseManager.register("livestreams")
BaseManager.register("streams")
BaseManager.register("categories")
BaseManager.register("follows")
BaseManager.register("import_follows")
BaseManager.register("get_live_streams")
BaseManager.register("get_categories")
BaseManager.register("get_category_streams")
BaseManager.register("get_channels")
BaseManager.register("update_db_streams")
BaseManager.register("update_db_categories")
m = BaseManager(address=("0.0.0.0", 50000), authkey=b"abc")
m.connect()
