#!/usr/bin/env python3
import subprocess
import xmlrpc.client
import argparse


class fzf:
    def no_search_result(self, type: str, command: list):
        """Menu to show when no results where found for the specific query"""
        command[-1] = type + " "
        if type != "streams":
            msg = f"no {type} found with that name (search another {type})"
        else:
            msg = "no streams found in that category (search another category)"
        selection = self.handle_selection(msg, command)
        if not selection:
            return
        if type == "channel":
            self.search_channel_menu(command)
        else:
            self.search_category_menu(command)
        return

    def follow_or_unfollow(self, type: str, selection: str, follow: bool):
        """Adds or removes a channel or category from the follows local databse"""
        global LIVESTREAMS, CATEGORIES
        if type == "channel":
            channel = selection.split()[0]
            LIVESTREAMS = CLIENT.update_db_streams(channel, follow)
        else:
            CATEGORIES = CLIENT.update_db_categories(selection, follow)
        return

    def call_rofi(self, entries: str, command: list):
        """Open rofi with the specified entries"""
        proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        proc.stdin.write((entries).encode("utf-8"))
        proc.stdin.close()
        answer = proc.stdout.read().decode("utf-8")
        proc.wait()
        answer = answer.replace("\n", "")
        exit_code = proc.returncode
        if "error_code" in answer:
            exit_code = int(answer.split("error_code")[0])
            answer = answer.split("error_code")[1]
        return answer, exit_code

    def handle_selection(self, entries: list, command: list, type=None):
        """Open the appropiate menu depending of the error code or return the selected item"""
        selection, error_code = self.call_rofi(entries, command)
        if error_code == 10:
            self.options_menu(command)
            return
        if error_code == 11:
            self.categories_menu(command)
            return
        if error_code == 12:
            self.livestreams_menu(command)
            return
        if error_code == 13:
            self.follow_or_unfollow(type, selection, True)
            selection = self.handle_selection(entries, command, type)
        elif error_code == 14:
            self.follow_or_unfollow(type, selection, False)
            selection = self.handle_selection(entries, command, type)
        return selection

    def import_menu(self, command: list):
        """Open the import followed channels menu"""
        command[-1] = "user name "
        command.append("--print-query")
        selection = self.handle_selection("", command, "channel")
        command.remove("--print-query")
        if not selection:
            return
        CLIENT.import_user_follows(selection)
        self.livestreams_menu(command)
        return

    def livestreams_menu(self, command: list):
        """Open the followed channels live streams menu"""
        command[-1] = "stream "
        selection = self.handle_selection(LIVESTREAMS, command, "channel")
        if not selection:
            return
        CLIENT.open_stream(selection, NO_CHAT)
        return

    def search_channel_menu(self, command: list):
        """Open the search channel menu"""
        command[-1] = "channel "
        command.append("--print-query")
        selection = self.handle_selection("", command)
        command.remove("--print-query")
        streams = CLIENT.get_channels(selection)
        if not streams:
            self.no_search_result("channel", command)
            return
        stream = self.handle_selection(streams, command, "channel")
        if not stream:
            return
        CLIENT.open_stream(stream, NO_CHAT)
        return

    def search_category_menu(self, command: list):
        """Open the search category menu"""
        command[-1] = "category "
        command.append("--print-query")
        selection = self.handle_selection("", command)
        command.remove("--print-query")
        categories = CLIENT.get_categories(selection)
        if not categories:
            self.no_search_result("category", command)
            return
        category = self.handle_selection(categories, command, "category")
        if not category:
            return
        streams = CLIENT.get_category_streams(category)
        if not streams:
            self.no_search_result("streams", command)
            return
        command[-1] = "channel "
        stream = self.handle_selection(streams, command, "channel")
        if not stream:
            return
        CLIENT.open_stream(stream, NO_CHAT)
        return

    def options_menu(self, command):
        """Open the options menu"""
        command[-1] = "option "
        options = [
            "search channel",
            "search category",
            "follow channel (exact match)",
            "follow category (exact match)",
            "import follows",
        ]
        options_string = "\n".join(options)
        selection = self.handle_selection(options_string, command)
        if not selection:
            return
        if "search channel" in selection:
            self.search_channel_menu(command)
        elif "search category" in selection:
            self.search_category_menu(command)
        elif "import" in selection:
            self.import_menu(command)
        elif "follow" in selection:
            selection = selection.split()
            type = selection[1]
            command[-1] = type
            selection = self.handle_selection("", command)
            if not selection:
                return
            self.follow_or_unfollow(type, selection, True)
        return

    def categories_menu(self, command: list):
        """Open the followed categories menu"""
        command[-1] = "category "
        selection = self.handle_selection(CATEGORIES, command)
        if not selection:
            return
        streams = CLIENT.get_category_streams(selection)
        command[-1] = "channel "
        stream = self.handle_selection(streams, command, "channel")
        if not stream:
            return
        CLIENT.open_stream(stream, NO_CHAT)
        return


class rofi(fzf):
    def import_menu(self, command: list):
        """Open the import followed channels menu"""
        command[-1] = "user name "
        selection = self.handle_selection("", command, "channel")
        if not selection:
            return
        CLIENT.import_user_follows(selection)
        self.livestreams_menu(command)
        return

    def search_channel_menu(self, command: list):
        """Open the search channel menu"""
        command[-1] = "channel"
        selection = self.handle_selection("", command)
        streams = CLIENT.get_channels(selection)
        if not streams:
            self.no_search_result("channel", command)
            return
        stream = self.handle_selection(streams, command, "channel")
        if not stream:
            return
        CLIENT.open_stream(stream, NO_CHAT)
        return


def search_category_menu(self, command: list):
    """Open the search category menu"""
    command[-1] = "category"
    selection = self.handle_selection("", command)
    categories = CLIENT.get_categories(selection)
    if not categories:
        self.no_search_result("category", command)
        return
    category = self.handle_selection(categories, command, "category")
    if not category:
        return
    streams = CLIENT.get_category_streams(category)
    if not streams:
        self.no_search_result("streams", command)
        return
    command[-1] = "channel"
    stream = self.handle_selection(streams, command, "channel")
    if not stream:
        return
    CLIENT.open_stream(stream, NO_CHAT)
    return


def main():
    global LIVESTREAMS, CATEGORIES, CLIENT, NO_CHAT
    keybindings = "alt+l: Followed Livestreams | alt+c: Followed Categories | alt+o: Options | alt+s: Follow selected item | alt+u: Unfollow selected item"
    parser = argparse.ArgumentParser(description="twofi")
    parser.add_argument(
        "-f", "--fzf", action="store_true", help="use fzf to show menus"
    )
    parser.add_argument("-C", "--no-chat", action="store_true", help="don't open chat")
    parser.add_argument("-H", "--host", default="localhost", help="daemon ip")
    args = parser.parse_args()
    FZF = args.fzf
    NO_CHAT=args.no_chat
    HOST= args.host
    CLIENT = xmlrpc.client.ServerProxy(f"http://{HOST}:9000", allow_none=True)
    LIVESTREAMS = CLIENT.livestreams()
    CATEGORIES = CLIENT.categories()

    if FZF:
        command = "fzf --reverse --border --header".split()
        command.append(keybindings)
        command.extend(["--bind=alt-o:execute(echo 10 error_code {})+abort"])
        command.extend(["--bind=alt-c:execute(echo 11 error_code {})+abort"])
        command.extend(["--bind=alt-l:execute(echo 12 error_code {})+abort"])
        command.extend(["--bind=alt-s:execute(echo 13 error_code {})+abort"])
        command.extend(["--bind=alt-u:execute(echo 14 error_code {})+abort"])
        command.extend("--prompt streams ".split())
        menu = fzf()
    else:
        command = "rofi -kb-custom-1 alt+o -kb-custom-2 alt+c -kb-custom-3 alt+l -kb-custom-4 alt+s -kb-custom-5 alt+u -dmenu -i -async-pre-read 1 -mesg ".split()
        command.append(keybindings)
        command.extend("-p streams".split())
        menu = rofi()

    menu.livestreams_menu(command)


if __name__ == "__main__":
    main()
