# twofi
Rofi script to launch twitch livestreams using streamlink and chatterino
![record](https://user-images.githubusercontent.com/98930451/186007335-2bc032fc-5053-4727-9dce-6f7a4408e008.gif)

### Features:
* Import your followed channels from your twitch account into a local database
* Add or remove channels to the local database
* Add or remove categories to the local database
* Search live channels and categories
* List all the current livestreams you follow
* List all the categories you follow and their current livestreams

### Instalation:
I recommend using pipx to install the program:
```
git clone https://github.com/Pecarvajal246/twofi.git
cd twofi
pipx install .
```
### Dependencies:

* [Rofi](https://github.com/davatorium/rofi)
* [Streamlink](https://github.com/streamlink/streamlink)
* [Chatterino](https://github.com/Chatterino/chatterino2)

### Usage:
Run the daemon:
```
twofi_d
```
And then run the command:
```
twofi
```
