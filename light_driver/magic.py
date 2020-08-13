import time

from play_status import PlayStatus
from protocol.base_controller import BaseController

BEAT_CLOSENESS_THRESHOLD = 0.1  # How close do we have to be to a beat (in time) in order to trigger a color change


class BasicLightDriver(object):
    def __init__(self, status: PlayStatus, controller: BaseController):
        self._ps = status
        self._next_bar = -1
        self.controller = controller

    def run(self):
        self._ps.lock.acquire()
        try:
            if self._ps.is_music_playing:
                sleep = self.poof()
            else:
                sleep = 3
        except KeyError as e:
            sleep = 1.5
        finally:
            self._ps.lock.release()
        time.sleep(sleep)

    def poof(self) -> float:  # There is no magic without a `poof`
        progress = self._ps.progress_sec + time.time() - self._ps.last_update - self._ps.response_delay / 2
        print("Beat! Progress: {}".format(progress))
        next_beat = None
        for beat in self._ps.audio_analysis["beats"]:
            if abs(beat["start"] - progress) <= BEAT_CLOSENESS_THRESHOLD:
                self.controller.beat(beat["duration"])
                continue
            if beat["start"] > progress:
                next_beat = beat
                break
        if next_beat:
            return next_beat["start"] - progress
        else:
            return 1.5

