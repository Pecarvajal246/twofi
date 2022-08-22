from twitchAPI.twitch import Twitch
import subprocess

def get_follows(user_id: str):
    """Gets the user's followed channels from the twitch api"""
    response = twitch.get_users_follows(first=100, from_id=user_id)
    total_follows = len(response["data"])
    follows = list()
    for i in range(total_follows):
        follows.append(response["data"][i]["to_login"])
    return follows


def get_live_streams(channels=None, channel_id=None, game_id=None):
    """Gets live streams from the twitch api for the user followed channels list, channel query or category query"""
    if channels:
        response = twitch.get_streams(first=100, user_login=channels)
    elif channel_id:
        response = twitch.get_streams(first=100, user_id=channel_id)
    else:
        response = twitch.get_streams(first=100, game_id=game_id)

    data = response["data"]
    streamers = [d["user_login"] for d in data]
    titles = [d["title"] for d in data]
    viewer_counts = [d["viewer_count"] for d in data]
    game_names = [d["game_name"] for d in data]
    streams = [
        f"{streamers[i]} | ({game_names[i]}) | {titles[i]} | ({viewer_counts[i]})"
        for i in range(len(streamers))
    ]
    return streams


def get_categories(query: str):
    """Gets categories that match the category query from the twitch api"""
    response = twitch.search_categories(query=query, first=100)
    data = response["data"]
    categories = [d["name"] for d in data]
    return categories


def get_category_streams(category: str):
    """Gets the live streams for a specific game id from the twitch api"""
    response = twitch.get_games(names=[category])
    game_id = response["data"][0]["id"]
    streams = get_live_streams(None, None, game_id)
    return streams


def get_channels(channel: str):
    """Gets the live streams that match the channel query from the twitch api"""
    response = twitch.search_channels(query=channel, first=100, live_only=True)
    data = response["data"]
    channels = [d["id"] for d in data]
    return channels


def import_user_follows(user: str):
    """Imports the followed channels from the users twitch account to the local database"""
    subprocess.run(["notify-send", f"Importing {user}'s followed streams"])
    loginInfo = twitch.get_users(logins=[user])
    user_id = loginInfo["data"][0]["id"]
    follows = get_follows(user_id)

    with config.open("w") as f:
        data["follows"] = {"channels": [], "categories": []}
        data["follows"]["channels"] = follows
        json.dump(data, f)

    subprocess.run(["notify-send", f"Finished importing {user}'s followed streams"])
    return follows

twitch = Twitch("2794znu5gmf9sjqla8fay7btcwwrja", "df2v3u00rfw9poset4qpj5g2ir255p")
