import asyncio
import requests
import spotipy
import os

from light_driver.magic import BasicLightDriver
from play_status import PlayStatus, PlayStatusUpdater
from protocol.yeelight import YeelightController


def main():
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope='user-read-currently-playing',
                                               cache_path=os.path.join(".spotify_caches", "cache.txt"),
                                               show_dialog=True)

    spotify = spotipy.Spotify(auth_manager=auth_manager)
    play_status = PlayStatus()
    status_updater = PlayStatusUpdater(spotify, play_status)
    status_updater.start()

    controller = YeelightController()
    basic = BasicLightDriver(play_status, controller)
    while True:
        basic.run()




main()




