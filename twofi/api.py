from twitchAPI.twitch import Twitch
from multiprocessing.managers import BaseManager
import threading
import time
import json
from pathlib import Path
from xdg.BaseDirectory import save_config_path

class api:
    """twofi api class"""
    def livestreams (self):
        """Sends the current livestreams to rofi"""
        return livestreams

    def categories(self):
        """Sends the categories to rofi"""
        return "\n".join(categories)

    def get_follows(self, user_id: str):
        """Gets the user's followed channels from the twitch api"""
        response = twitch.get_users_follows(first=100, from_id=user_id)
        total_follows = len(response["data"])
        follows = list()
        for i in range(total_follows):
            follows.append(response["data"][i]["to_login"])
        return follows


    def get_live_streams(self, channels=None, channel_id=None, game_id=None):
        """Gets live streams from the twitch api for the user followed channels list, channel query or category query"""
        if channels:
            response = twitch.get_streams(first=100, user_login=channels)
        elif channel_id:
            response = twitch.get_streams(first=100, user_id=channel_id)
        elif game_id:
            response = twitch.get_streams(first=100, game_id=game_id)
        else:
            response = twitch.get_streams(first=100)

        data = response["data"]
        streamers = [d["user_login"] for d in data]
        titles = [d["title"] for d in data]
        viewer_counts = [d["viewer_count"] for d in data]
        game_names = [d["game_name"] for d in data]
        streams = [
            f"{streamers[i]} | {titles[i]} | {game_names[i]} | ({viewer_counts[i]})"
            for i in range(len(streamers))
        ]
        streams_string = "\n".join(streams)
        return streams_string


    def get_categories(self, query=None):
        """Gets categories that match the category query from the twitch api"""
        if query:
            response = twitch.search_categories(query=query, first=100)
        else:
            response = twitch.get_top_games(first=100)
        data = response["data"]
        categories = [d["name"] for d in data]
        if not categories:
            return False
        categories_string = "\n".join(categories)
        return categories_string


    def get_category_streams(self, category: str):
        """Gets the live streams for a specific game id from the twitch api"""
        response = twitch.get_games(names=[category])
        game_id = response["data"][0]["id"]
        streams = self.get_live_streams(None, None, game_id)
        return streams


    def get_channels(self, channel: str):
        """Gets the live streams that match the channel query from the twitch api"""
        response = twitch.search_channels(query=channel, first=100, live_only=True)
        data = response["data"]
        channels = [d["id"] for d in data]
        if not channels:
            return False
        live_channels= self.get_live_streams(None, channels, None)
        return live_channels


    def import_user_follows(self, user: str):
        """Imports the followed channels from the users twitch account to the local database"""
        login_info = twitch.get_users(logins=[user])
        user_id = login_info["data"][0]["id"]
        follows = self.get_follows(user_id)
        follows = [follow for follow in follows if follow not in streams]
        streams.extend(follows)
        with config.open("w") as f:
            data["follows"]["channels"] = streams
            json.dump(data, f)
        return follows


    def update_db_streams(self, channel: str, follow: bool):
        """Updates the followed streams database"""
        global streams, livestreams
        if follow:
            streams.append(channel)
        else:
            streams.remove(channel)
        livestreams = self.get_live_streams(streams)
        with config.open("w") as f:
            data["follows"]["channels"] = streams
            json.dump(data, f)


    def update_db_categories(self, category: str, follow: bool):
        """Updates the followed categories database"""
        global categories
        if follow:
            categories.append(category)
        else:
            categories.remove(category)
        with config.open("w") as f:
            data["follows"]["categories"] = categories
            json.dump(data, f)


twitch = Twitch("2794znu5gmf9sjqla8fay7btcwwrja", "df2v3u00rfw9poset4qpj5g2ir255p")


def livestreams_thread():
    """Query for livestreams every 30 seconds"""
    global livestreams, streams
    while True:
        if streams:
            livestreams = api.get_live_streams(api,streams)
            time.sleep(30)
        else:
            time.sleep(1)
    return livestreams


def main():
    global livestreams, streams, categories, config, data
    path = Path(save_config_path("twofi"))
    config = path.joinpath("user_data.json")
    if config.is_file():
        with config.open("r+") as f:
            data = json.load(f)
    else:
        with config.open("w+") as f:
            data = {"follows": {"channels": [], "categories": []}}
            json.dump(data, f)
    streams = data["follows"]["channels"]
    categories = data["follows"]["categories"]
    categories.sort()
    livestreams = None
    x = threading.Thread(target=livestreams_thread, args=())
    x.start()
    BaseManager.register("api", api)
    manager = BaseManager(address=("0.0.0.0", 50000), authkey=b"abc")
    server = manager.get_server()
    server.serve_forever()


if __name__ == "__main__":
    main()
