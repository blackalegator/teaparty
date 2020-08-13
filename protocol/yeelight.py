import threading
import queue
import random
import time

from yeelight import *

from protocol.base_controller import BaseController

MIN_DELAY = 3  # Minimum delay in seconds between color change


class YeelightController(BaseController):
    def __init__(self):
        self.bulbs = [YeelightBulb("192.168.3.53")]
        for bulb in self.bulbs:
            bulb.start()

    def beat(self, duration):
        bulbs = list.copy(self.bulbs)
        random.shuffle(bulbs)
        now = time.time()
        for bulb in bulbs:
            if now - MIN_DELAY >= bulb.get_last_change():
                bulb.next_color(duration)


class YeelightBulb(threading.Thread):
    colors = [(204,0,0), (255,0,102), (153, 51, 255)]
    random.shuffle(colors)

    def __init__(self, ip_address):
        super().__init__()
        self.ip_address = ip_address
        self.bulb = Bulb(ip_address)
        self.bulb.start_music()
        self.q = queue.Queue()
        self.next_color_index = 0
        self.last_change = 0

    def get_last_change(self) -> float :
        return self.last_change

    # Duration comes in seconds, we need ms for yeelight command
    def next_color(self, duration):
        self.last_change = time.time()
        self.q.put(duration * 1000)

    def run(self):
        while True:
            duration = self.q.get()
            if self.next_color_index > len(YeelightBulb.colors) - 1:
                self.next_color_index = 0
            color = YeelightBulb.colors[self.next_color_index]
            self.next_color_index += 1
            # transitions = [RGBTransition(*color, duration=duration)]
            # flow = Flow(count=0, transitions=transitions)
            # self.bulb.start_flow(flow)
            self.bulb.set_rgb(*color)
            print("Color change on {}".format(self.ip_address))
            self.q.task_done()
