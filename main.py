from twitchAPI.twitch import Twitch
import subprocess
import json

twitch = Twitch('2794znu5gmf9sjqla8fay7btcwwrja', 'df2v3u00rfw9poset4qpj5g2ir255p')

def get_follows(user_id: str):
    response=twitch.get_users_follows(first=100, from_id=user_id)
    total_follows=len(response['data'])
    follows=list()

    for i in range(total_follows):
        follows.append(response['data'][i]['to_login'])

    return follows

def import_user_follows(data: dict, user_id: str):
    follows=get_follows(user_id)

    with open("user_data.json", "w") as f:
        data["follows"]={"channels":[], "categories":[]}
        data["follows"]["channels"]=follows
        json.dump(data, f)

    return follows

def get_live_streams(follows):
    response=twitch.get_streams(first=100, user_login=follows)
    data=response['data']
    streamers=[d['user_login'] for d in data]
    titles=[d['title'] for d in data]
    viewer_counts=[d['viewer_count'] for d in data]
    streams=[f"{streamers[i]} {titles[i]} {viewer_counts[i]}" for i in range(len(streamers))]
    return streams

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

def open_stream(stream: str):
    kill_process(['mpv', 'chatterino'])
    stream=stream.split()[0]
    subprocess.Popen(['chatterino', '-c', stream], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    subprocess.Popen(['streamlink', f'https://www.twitch.tv/{stream}'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)

def kill_process(programs: list):
    for program in programs:
        running=subprocess.run(['pgrep', program], capture_output=True)
        if running:
            subprocess.run(['killall', program])

def handle_selection(selection: str, error_code: int):
    if error_code == 0:
        open_stream(selection)
    elif error_code == 10:
        options_menu(livestreams)

def livestreams_menu(livestreams: list):
    command='rofi -font xos4terminus 12 -bw 3 -kb-custom-1 ctrl+o -kb-custom-2 alt+u -dmenu -i -p wtwitch'.split()
    selected_stream, error_code=call_rofi(livestreams, command)
    handle_selection(selected_stream, error_code)

def search_menu(search):
    options=[]
    command=f'rofi -font xos4terminus 12 -bw 3 -kb-custom-1 ctrl+o -kb-custom-2 alt+u -dmenu -i -p {search}'.split()
    selection, error_code=call_rofi(options, command)


def options_menu(livestreams: list):
    options=['search channel', 'search category', 'follow channel', 'follow category','go back']
    command='rofi -font xos4terminus 12 -bw 3 -kb-custom-1 ctrl+o -kb-custom-2 alt+u -dmenu -i -p options'.split()
    selection, error_code=call_rofi(options, command)

    if selection == 'go back':
        livestreams_menu(livestreams)
    elif 'search' in selection:
        search_menu(selection.split()[1])


with open("user_data.json", "r") as f:
    data = json.load(f)

user=data["login"]

if "follows" not in data:
    loginInfo=twitch.get_users(logins=[user])
    user_id=loginInfo['data'][0]['id']
    follows=import_user_follows(data, user_id)

else:
    follows=data["follows"]["channels"]

livestreams=get_live_streams(follows)
livestreams_menu(livestreams)
