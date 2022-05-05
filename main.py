from twitchAPI.twitch import Twitch
import subprocess
import json

def get_follows(user_id: str):
    """Gets the user's followed channels from the twitch api"""
    response=twitch.get_users_follows(first=100, from_id=user_id)
    total_follows=len(response['data'])
    follows=list()

    for i in range(total_follows):
        follows.append(response['data'][i]['to_login'])

    return follows


def get_live_streams(channels=None, channel_id=None, game_id=None):
    """Gets live streams from the twitch api for the user followed channels list, channel query or category query"""

    if channels:
        response=twitch.get_streams(first=100, user_login=channels)

    elif channel_id:
        response=twitch.get_streams(first=100, user_id=channel_id)

    else:
        response=twitch.get_streams(first=100, game_id=game_id)

    data=response['data']
    streamers=[d['user_login'] for d in data]
    titles=[d['title'] for d in data]
    viewer_counts=[d['viewer_count'] for d in data]
    streams=[f"{streamers[i]} {titles[i]} {viewer_counts[i]}" for i in range(len(streamers))]
    return streams


def no_search_result(type: str):
    """Menu to show when no results where found for the specific query"""
    command[-1]=type
    if type != 'streams':
        msg=[f'no {type} found with that name (search another {type})', 'return to options', 'return to livestreams']
    else:
        msg=['no streams found in that category (search another category)', 'return to options', 'return to livestreams']

    selection=handle_selection(msg, command)
    if not selection: return

    if 'another' in selection:

        if type == 'channel':
            search_channel_menu(command)

        else:
            search_category_menu(command)

    elif 'options' in selection:
        options_menu()

    else:
        livestreams_menu(livestreams)

    return


def get_categories(query: str):
    """Gets categories that match the category query from the twitch api"""
    response=twitch.search_categories(query=query, first=100)
    data= response['data']
    categories=[d['name'] for d in data]
    return categories


def get_category_streams(category: str):
    """Gets the live streams for a specific game id from the twitch api"""
    response=twitch.get_games(names=[category])
    game_id=response['data'][0]['id']
    streams=get_live_streams(None, None, game_id)
    return streams


def get_channels(channel: str):
    """Gets the live streams that match the channel query from the twitch api"""
    response=twitch.search_channels(query=channel, first=100, live_only=True)
    data= response['data']
    channels=[d['id'] for d in data]
    return channels


def import_user_follows(data: dict):
    """Imports the followed channels from the users twitch account to the local database"""
    user=data["login"]
    loginInfo=twitch.get_users(logins=[user])
    user_id=loginInfo['data'][0]['id']
    follows=get_follows(user_id)

    with open("user_data.json", "w") as f:
        data["follows"]={"channels":[], "categories":[]}
        data["follows"]["channels"]=follows
        json.dump(data, f)

    return follows


def add_follow(type: str, follow: str):
    """Adds a channel or category to the follows local databse"""
    if type == 'channel':
        follows=data["follows"]["channels"]
        follows.append(follow)

        with open("user_data.json", "w") as f:
            data["follows"]["channels"]=follows
            json.dump(data, f)

    else:
        follows=data["follows"]["categories"]
        follows.append(follow)

        with open("user_data.json", "w") as f:
            data["follows"]["categories"]=follows
            json.dump(data, f)

    subprocess.run(['notify-send', f'added {follow} to follows list'])
    return


def open_stream(stream: str):
    """Open the selected channel's stream in mpv and chat in chatterino"""
    kill_process(['mpv', 'chatterino'])
    stream=stream.split()[0]
    subprocess.run(['notify-send', f"Launching {stream}'s stream"])
    subprocess.Popen(['chatterino', '-c', stream], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    subprocess.Popen(['streamlink', f'https://www.twitch.tv/{stream}'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    return


def kill_process(programs: list):
    """Kill any instance of a program running"""
    for program in programs:
        running=subprocess.run(['pgrep', program], capture_output=True)
        if running:
            subprocess.run(['killall', program])


def call_rofi(entries: list, command: list):
    """Open rofi with the specified entries"""
    proc = subprocess.Popen(command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE)
    for e in entries:
        proc.stdin.write((e+"\n").encode('utf-8'))
    proc.stdin.close()
    answer = proc.stdout.read().decode('utf-8')
    proc.wait()
    exit_code = proc.returncode
    return answer.replace("\n",""), exit_code

def handle_selection(entries: list, command: list):
    """Open the appropiate menu depending of the error code or return the selected item"""
    selection, error_code=call_rofi(entries, command)
    if error_code == 10:
        options_menu()
        return

    elif error_code == 11:
        categories_menu(command)
        return

    elif error_code == 12:
        livestreams_menu(livestreams)
        return

    return selection


def livestreams_menu(livestreams: list):
    """Open the followed channels live streams menu"""
    selection=handle_selection(livestreams, command)
    if not selection: return
    open_stream(selection)
    return


def search_channel_menu(command: list):
    """Open the search channel menu"""
    command[-1]='channel'
    selection=handle_selection([], command)
    if not selection: return
    channels=get_channels(selection)

    if not channels:
        no_search_result('channel')
        return

    streams=get_live_streams(None, channels, None)
    stream=handle_selection(streams, command)
    if not stream: return
    open_stream(stream)
    return


def search_category_menu(command: list):
    """Open the search category menu"""
    command[-1]='category'
    selection=handle_selection([], command)
    if not selection: return
    categories=get_categories(selection)
    if not categories:
        no_search_result('category')
        return
    category=handle_selection(categories, command)
    if not category: return
    streams=get_category_streams(category)
    if not streams:
        no_search_result('streams')
        return
    command[-1]='channel'
    stream=handle_selection(streams, command)
    if not stream: return
    open_stream(stream)
    return


def options_menu():
    """Open the options menu"""
    options=['search channel', 'search category', 'follow channel', 'follow category','go to livestreams', 'go to followed categories']
    selection=handle_selection(options, command)
    if not selection: return

    elif 'livestreams' in selection:
        livestreams_menu(livestreams)

    elif 'followed' in selection:
        categories_menu(command)

    elif 'search channel' in selection:
        search_channel_menu(command)

    elif 'search category' in selection:
        search_category_menu(command)

    elif 'follow' in selection:
        selection=selection.split()
        type=selection[1]
        command[-1]=type
        selection=handle_selection([], command)
        if not selection: return
        add_follow(type, selection)

    return

def categories_menu(command: list):
    """Open the followed categories menu"""
    command[-1]='category'
    selection=handle_selection(categories, command)
    if not selection: return
    streams=get_category_streams(selection)
    command[-1]='channel'
    stream=handle_selection(streams, command)
    if not stream: return
    open_stream(stream)
    return

print('authenticating app')
twitch = Twitch('2794znu5gmf9sjqla8fay7btcwwrja', 'df2v3u00rfw9poset4qpj5g2ir255p')

with open("user_data.json", "r") as f:
    data = json.load(f)


if "follows" in data:
    streams=data["follows"]["channels"]
    categories=data["follows"]["categories"]

else:
    streams=import_user_follows(data)

command='rofi -font xos4terminus 12 -bw 3 -kb-custom-1 ctrl+o -kb-custom-2 ctrl+c -kb-custom-3 ctrl+s -dmenu -i -p streams'.split()
print('getting live streams')
livestreams=get_live_streams(streams)
livestreams_menu(livestreams)
