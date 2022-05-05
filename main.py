from twitchAPI.twitch import Twitch
import subprocess
import json

def get_follows(user_id: str):
    response=twitch.get_users_follows(first=100, from_id=user_id)
    total_follows=len(response['data'])
    follows=list()

    for i in range(total_follows):
        follows.append(response['data'][i]['to_login'])

    return follows


def get_live_streams(channels=None, channel_id=None, game_id=None):

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
    command[-1]=type
    msg=[f'no {type} found with that name (search another {type})', 'return to options', 'return to livestreams']
    selection, error_code=call_rofi(msg, command)
    if not selection: return

    if 'another' in selection:

        if type == 'channel':
            search_channel(command)

        else:
            search_category(command)

    elif 'options' in selection:
        options_menu()

    else:
        livestreams_menu(livestreams)

    return


def get_categories(query: str):
    response=twitch.search_categories(query=query, first=100)
    data= response['data']
    categories=[d['name'] for d in data]
    return categories


def get_category_streams(category: str):
    response=twitch.get_games(names=[category])
    game_id=response['data'][0]['id']
    streams=get_live_streams(None, None, game_id)
    return streams


def get_channels(channel: str):
    response=twitch.search_channels(query=channel, first=100, live_only=True)
    data= response['data']
    channels=[d['id'] for d in data]
    return channels


def import_user_follows(data: dict):
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
    kill_process(['mpv', 'chatterino'])
    stream=stream.split()[0]
    subprocess.run(['notify-send', f"Launching {stream}'s stream"])
    subprocess.Popen(['chatterino', '-c', stream], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    subprocess.Popen(['streamlink', f'https://www.twitch.tv/{stream}'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    return


def kill_process(programs: list):
    for program in programs:
        running=subprocess.run(['pgrep', program], capture_output=True)
        if running:
            subprocess.run(['killall', program])


def call_rofi(entries: list, command: list):
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

def handle_error_code(error_code: int):
    if error_code == 10:
        options_menu()

    elif error_code == 11:
        categories_menu(command)

    elif error_code == 12:
        livestreams_menu(livestreams)

    return


def livestreams_menu(livestreams: list):
    selection, error_code=call_rofi(livestreams, command)
    if not selection: return

    if error_code != 0:
        handle_error_code(error_code)
        return

    open_stream(selection)
    return


def search_channel(command: list):
    command[-1]='channel'
    selection, error_code=call_rofi([], command)
    if error_code != 0:
        handle_error_code(error_code)
        return

    channels=get_channels(selection)

    if not channels:
        no_search_result('channel')
        return

    streams=get_live_streams(None, channels, None)
    stream, error_code=call_rofi(streams, command)
    if error_code != 0:
        handle_error_code(error_code)
        return

    if not stream: return
    open_stream(stream)
    return


def search_category(command: list):
    command[-1]='category'
    selection, error_code=call_rofi([], command)
    if error_code != 0:
        handle_error_code(error_code)
        return

    if not selection: return

    categories=get_categories(selection)
    if not categories:
        no_search_result('category')
        return
    category, error_code=call_rofi(categories, command)

    if error_code != 0:
        handle_error_code(error_code)
        return

    if not category: return
    streams=get_category_streams(category)
    command[-1]='channel'
    stream, error_code=call_rofi(streams, command)

    if error_code != 0:
        handle_error_code(error_code)
        return

    if not stream: return
    open_stream(stream)
    return


def options_menu():
    options=['search channel', 'search category', 'follow channel', 'follow category','go to livestreams', 'go to followed categories']
    # command='rofi -font xos4terminus 12 -bw 3 -dmenu -i -p options'.split()
    selection, error_code=call_rofi(options, command)

    if error_code != 0:
        handle_error_code(error_code)
        return

    if not selection: return

    elif 'livestreams' in selection:
        livestreams_menu(livestreams)

    elif 'followed' in selection:
        categories_menu(command)

    elif 'search channel' in selection:
        search_channel(command)

    elif 'search category' in selection:
        search_category(command)

    elif 'follow' in selection:
        selection=selection.split()
        type=selection[1]
        command[-1]=type
        selection, error_code=call_rofi([], command)
        if error_code != 0:
            handle_error_code(error_code)
            return
        add_follow(type, selection)

    return

def categories_menu(command: list):
    command[-1]='category'
    selection, error_code=call_rofi(categories, command)

    if error_code != 0:
        handle_error_code(error_code)
        return

    if not selection: return
    streams=get_category_streams(selection)
    command[-1]='channel'
    stream, error_code=call_rofi(streams, command)

    if error_code != 0:
        handle_error_code(error_code)
        return

    if not stream: return
    open_stream(stream)
    return


twitch = Twitch('2794znu5gmf9sjqla8fay7btcwwrja', 'df2v3u00rfw9poset4qpj5g2ir255p')

with open("user_data.json", "r") as f:
    data = json.load(f)


if "follows" not in data:
    streams=import_user_follows(data)

else:
    streams=data["follows"]["channels"]
    categories=data["follows"]["categories"]

command='rofi -font xos4terminus 12 -bw 3 -kb-custom-1 ctrl+o -kb-custom-2 ctrl+c -kb-custom-3 ctrl+s -dmenu -i -p streams'.split()
livestreams=get_live_streams(streams)
livestreams_menu(livestreams)
