from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
import threading
import time
import json
import subprocess
from pathlib import Path
from xdg.BaseDirectory import save_config_path
from twitchAPI.twitch import Twitch


class Api:
    """twofi api class"""

    def livestreams(self):
        """Sends the current livestreams to rofi"""
        return LIVESTREAMS

    def categories(self):
        """Sends the categories to rofi"""
        return "\n".join(CATEGORIES)

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
            streams_data = {}
            streams_list = []
        elif channel_id:
            response = twitch.get_streams(first=100, user_id=channel_id)
        elif game_id:
            response = twitch.get_streams(first=100, game_id=game_id)
        else:
            response = twitch.get_streams(first=100)

        data = response["data"]
        streams_string = str()
        for stream in data:
            if channels:
                streams_data[stream["user_login"]] = {
                    "title": stream["title"],
                    "viewer_count": stream["viewer_count"],
                    "game_name": stream["game_name"],
                    "thumbnail": stream["thumbnail_url"],
                }
                streams_list.append(stream["user_login"])

            streams_string += f"{stream['user_login']} | {stream['title']} | {stream['game_name']} | ({stream['viewer_count']})\n"

        if channels:
            return streams_data, streams_list, streams_string

        return streams_string

    def get_categories(self, query: str):
        """Gets categories that match the category query from the twitch api"""
        if not query:
            response = twitch.get_top_games(first=100)
        else:
            response = twitch.search_categories(query=query, first=100)
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
        streams = self.get_live_streams(game_id=game_id)
        return streams

    def get_channels(self, channel: str):
        """Gets the live streams that match the channel query from the twitch api"""
        if not channel:
            return self.get_live_streams()
        response = twitch.search_channels(query=channel, first=100, live_only=True)
        data = response["data"]
        channels = [d["id"] for d in data]
        if not channels:
            return False
        live_channels = self.get_live_streams(channel_id=channels)
        return live_channels

    def import_user_follows(self, user: str):
        """Imports the followed channels from the users twitch account to the local database"""
        subprocess.run(["notify-send", f"Importing {user}'s followed streams"])
        login_info = twitch.get_users(logins=[user])
        user_id = login_info["data"][0]["id"]
        follows = self.get_follows(user_id)
        follows = [follow for follow in follows if follow not in STREAMS]
        STREAMS.extend(follows)
        _, _, LIVESTREAMS= self.get_live_streams(STREAMS)
        with CONFIG.open("w") as f:
            DATA["follows"]["channels"] = STREAMS
            json.dump(DATA, f)
        subprocess.run(
            ["notify-send", f"Finished importing {user}'s followed streams"]
        )
        subprocess.run(["notify-send", f"Added {follows} to database"])
        return

    def update_db_streams(self, channel: str, follow: bool):
        """Updates the followed streams database"""
        global STREAMS, LIVESTREAMS
        if follow:
            STREAMS.append(channel)
            subprocess.run(["notify-send", f"added {channel} to follows list"])
        else:
            STREAMS.remove(channel)
            subprocess.run(["notify-send", f"removed {channel} from follows list"])
        _, _, LIVESTREAMS = self.get_live_streams(STREAMS)
        with CONFIG.open("w") as f:
            DATA["follows"]["channels"] = STREAMS
            json.dump(DATA, f)
        return LIVESTREAMS

    def update_db_categories(self, category: str, follow: bool):
        """Updates the followed categories database"""
        global CATEGORIES
        if follow:
            CATEGORIES.append(category)
            subprocess.run(["notify-send", f"added {category} to follows list"])
        else:
            CATEGORIES.remove(category)
            subprocess.run(["notify-send", f"removed {category} from follows list"])
        with CONFIG.open("w") as f:
            DATA["follows"]["categories"] = CATEGORIES
            json.dump(DATA, f)
        CATEGORIES.sort()
        return '\n'.join(CATEGORIES)

    def notifications(self, streams_data: dict, new_streams: str):
        for stream in new_streams:
            title=streams_data[stream]["title"]
            game_name=streams_data[stream]["game_name"]
            command = [
                "notify-send",
                f"{stream} is live!",
                f"{title}\n{game_name}"
            ]
            subprocess.run(command)

    def open_stream(self, stream: str):
        """Open the selected channel's stream in mpv and chat in chatterino"""
        self.kill_process(["mpv", "chatterino"])
        stream = stream.split()[0]
        subprocess.run(["notify-send", f"Launching {stream}'s stream"])
        subprocess.Popen(
            ["chatterino", "-c", stream],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        subprocess.Popen(
            ["streamlink", f"https://www.twitch.tv/{stream}"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        return

    def kill_process(self, programs: list):
        """Kill any instance of a program running"""
        for program in programs:
            running = subprocess.run(["pgrep", program], capture_output=True)
            if running.stdout:
                subprocess.run(["killall", program])


def livestreams_thread():
    """Query for livestreams every 30 seconds"""
    global LIVESTREAMS, STREAMS, LIVESTREAMS_LIST
    while True:
        if STREAMS:
            api=Api()
            streams_data, streams_list, LIVESTREAMS = api.get_live_streams(STREAMS)
            new_streams = set(streams_list).difference(set(LIVESTREAMS_LIST))
            LIVESTREAMS_LIST = streams_list
            if new_streams:
                api.notifications(streams_data, new_streams)
            time.sleep(30)
        else:
            time.sleep(1)


def main():
    global LIVESTREAMS, STREAMS, CATEGORIES, CONFIG, DATA, LIVESTREAMS_LIST
    path = Path(save_config_path("twofi"))
    CONFIG = path.joinpath("user_data.json")
    if CONFIG.is_file():
        with CONFIG.open("r+") as f:
            DATA = json.load(f)
    else:
        with CONFIG.open("w+") as f:
            DATA = {"follows": {"channels": [], "categories": []}}
            json.dump(DATA, f)
    STREAMS = DATA["follows"]["channels"]
    CATEGORIES = DATA["follows"]["categories"]
    CATEGORIES.sort()
    LIVESTREAMS_LIST = []
    x = threading.Thread(target=livestreams_thread, args=())
    x.start()
    with SimpleXMLRPCServer(
        ("localhost", 8000), requestHandler=SimpleXMLRPCRequestHandler, allow_none=True
    ) as server:
        server.register_instance(Api())
        server.serve_forever()


twitch = Twitch("2794znu5gmf9sjqla8fay7btcwwrja", "df2v3u00rfw9poset4qpj5g2ir255p")
if __name__ == "__main__":
    main()
