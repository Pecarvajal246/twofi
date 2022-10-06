#!/usr/bin/env python3
import subprocess
from twofi import client

def no_search_result(type: str, command: list):
    """Menu to show when no results where found for the specific query"""
    command[-1] = type
    if type != "streams":
        msg = f"no {type} found with that name (search another {type})"
    else:
        msg = "no streams found in that category (search another category)"
    selection = handle_selection(msg, command)
    if not selection:
        return
    if type == "channel":
        search_channel_menu(command)
    else:
        search_category_menu(command)
    return


def follow_or_unfollow(type: str, selection: str, follow: bool):
    """Adds or removes a channel or category from the follows local databse"""
    global livestreams, categories
    if type == "channel":
        channel = selection.split()[0]
        if follow:
            subprocess.run(["notify-send", f"added {channel} to follows list"])
        else:
            subprocess.run(["notify-send", f"removed {channel} from follows list"])
        client.update_db_streams(channel, follow)
        livestreams = client.livestreams()
    else:
        followed_categories = client.categories()
        if follow:
            subprocess.run(["notify-send", f"added {selection} to follows list"])
        else:
            subprocess.run(["notify-send", f"removed {selection} from follows list"])
        client.update_db_categories(selection, follow)
        categories = client.categories()
    return


def open_stream(stream: str):
    """Open the selected channel's stream in mpv and chat in chatterino"""
    kill_process(["mpv", "chatterino"])
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


def kill_process(programs: list):
    """Kill any instance of a program running"""
    for program in programs:
        running = subprocess.run(["pgrep", program], capture_output=True)
        if running:
            subprocess.run(["killall", program])


def call_rofi(entries: str, command: list):
    """Open rofi with the specified entries"""
    proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    proc.stdin.write((entries).encode("utf-8"))
    proc.stdin.close()
    answer = proc.stdout.read().decode("utf-8")
    proc.wait()
    exit_code = proc.returncode
    return answer.replace("\n", ""), exit_code


def handle_selection(entries: list, command: list, type=None):
    """Open the appropiate menu depending of the error code or return the selected item"""
    selection, error_code = call_rofi(entries, command)
    if error_code == 10:
        options_menu(command)
        return
    elif error_code == 11:
        categories_menu(command)
        return
    elif error_code == 12:
        livestreams_menu(command)
        return
    elif error_code == 13:
        follow_or_unfollow(type, selection, True)
        selection = handle_selection(entries, command, type)
    elif error_code == 14:
        follow_or_unfollow(type, selection, False)
        selection = handle_selection(entries, command, type)
    return selection


def import_menu(command: list):
    """Open the import followed channels menu"""
    command[-1] = "user name"
    selection = handle_selection("", command, "channel")
    if not selection:
        return
    subprocess.run(["notify-send", f"Importing {selection}'s followed streams"])
    new_follows = client.import_user_follows(selection)
    subprocess.run(
        ["notify-send", f"Finished importing {selection}'s followed streams"]
    )
    subprocess.run(["notify-send", f"Added {new_follows} to database"])
    return


def livestreams_menu(command: list):
    """Open the followed channels live streams menu"""
    selection = handle_selection(livestreams, command, "channel")
    if not selection:
        return
    open_stream(selection)
    return


def search_channel_menu(command: list):
    """Open the search channel menu"""
    command[-1] = "channel"
    selection = handle_selection("", command)
    if not selection:
        streams = client.get_live_streams(None, None, None)
    else:
        streams = client.get_channels(selection)
        if not streams:
            no_search_result("channel", command)
            return
    stream = handle_selection(streams, command, "channel")
    if not stream:
        return
    open_stream(stream)
    return


def search_category_menu(command: list):
    """Open the search category menu"""
    command[-1] = "category"
    selection = handle_selection("", command)
    if not selection:
        categories = client.get_categories(None)
    else:
        categories = client.get_categories(selection)
    if not categories:
        no_search_result("category", command)
        return
    category = handle_selection(categories, command, "category")
    if not category:
        return
    streams = client.get_category_streams(category)
    if not streams:
        no_search_result("streams", command)
        return
    command[-1] = "channel"
    stream = handle_selection(streams, command, "channel")
    if not stream:
        return
    open_stream(stream)
    return


def options_menu(command):
    """Open the options menu"""
    options = [
        "search channel",
        "search category",
        "follow channel (exact match)",
        "follow category (exact match)",
        "import follows",
    ]
    options_string= '\n'.join(options)
    selection = handle_selection(options_string, command)
    if not selection:
        return
    elif "search channel" in selection:
        search_channel_menu(command)
    elif "search category" in selection:
        search_category_menu(command)
    elif "import" in selection:
        import_menu(command)
    elif "follow" in selection:
        selection = selection.split()
        type = selection[1]
        command[-1] = type
        selection = handle_selection("", command)
        if not selection:
            return
        follow_or_unfollow(type, selection, True)
    return


def categories_menu(command: list):
    """Open the followed categories menu"""
    command[-1] = "category"
    selection = handle_selection(categories, command)
    if not selection:
        return
    streams = client.get_category_streams(selection)
    command[-1] = "channel"
    stream = handle_selection(streams, command, "channel")
    if not stream:
        return
    open_stream(stream)
    return


def main():
    global livestreams, categories
    keybindings = "alt+l: Followed Livestreams | alt+c: Followed Categories | alt+o: Options | alt+s: Follow selected item | alt+u: Unfollow selected item"
    command = "rofi -kb-custom-1 alt+o -kb-custom-2 alt+c -kb-custom-3 alt+l -kb-custom-4 alt+s -kb-custom-5 alt+u -dmenu -i -async-pre-read 1 -mesg ".split()
    command.append(keybindings)
    command.extend("-p streams".split())
    livestreams = client.livestreams()
    categories = client.categories()

    livestreams_menu(command)


if __name__ == "__main__":
    main()
