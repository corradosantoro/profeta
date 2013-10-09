#
# sensor.py
#

import threading
import Queue

from profeta.lib import *


class AsyncSensorProxy(Sensor, threading.Thread):

    def __init__(self, uSyncSensor):
        Sensor.__init__(self)
        threading.Thread.__init__(self)
        self.__sensor = uSyncSensor
        self.__queue = Queue.Queue(1)
        self.start()

    def sense(self):
        try:
            e = self.__queue.get_nowait()
            return e
        except Queue.Empty:
            return None

    # thread context
    def run(self):
        while True:
            e = self.__sensor.sense()
            if e is not None:
                self.__queue.put(e)

