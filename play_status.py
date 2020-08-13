import threading
import time

import spotipy

RESPONSE_DELAY_THRESHOLD = 0.1  # If a response delay is this times better update track progress


class PlayStatus(object):
    def __init__(self):
        # Time we received response at. Subtract last response time/2 for better approx of progress
        self.last_update: float = 0
        self.progress_sec: float = 0.0
        self.is_music_playing: bool = False
        self.item: dict = {"id": None}
        self.response_delay = 1000
        self.audio_analysis: dict = {}
        self.audio_features: dict = {}
        self.lock = threading.Lock()


class PlayStatusUpdater(threading.Thread):
    def __init__(self, spotify: spotipy.Spotify, play_status: PlayStatus):
        super().__init__()
        self._spotify = spotify
        self._ps = play_status

    def run(self):
        try:
            while True:
                self.update()
                time.sleep(1)
        except KeyboardInterrupt:
            pass

    def update(self):
        is_new_track = False
        progress_update_required = False
        start = time.time()  # Everything is in milliseconds
        status = self._spotify.current_playback()
        end = time.time()
        self._ps.lock.acquire()  # Do not forget the locks!
        if self._ps.item["id"] != status["item"]["id"]:
            is_new_track = True

        self._ps.is_music_playing = status["is_playing"] and status["item"]["type"] == "track"

        if is_new_track:
            self._ps.item = status["item"]
            progress_update_required = True
            if self._ps.item["type"] == "track":
                print("New track is playing: {}".format(self._ps.item["name"]))
                self._ps.audio_analysis = self._spotify.audio_analysis(self._ps.item["id"])
                self._ps.audio_features = self._spotify.audio_features(self._ps.item["id"])

        response_delay = end - start
        if response_delay / self._ps.response_delay < RESPONSE_DELAY_THRESHOLD:
            progress_update_required = True

        if progress_update_required:
            self._ps.response_delay = response_delay
            self._ps.last_update = end  # When did we last update track progress
            self._ps.progress_sec = status["progress_ms"] / 1000

        self._ps.lock.release()  # Don't forget to release the lock!
