#
# sensor.py
#

import threading
import Queue

from profeta.lib import *


class AsyncSensorProxy(Sensor):

    def __init__(self, uSyncSensor):
        Sensor.__init__(self)
        self.__sensor = uSyncSensor
        self.__queue = Queue.Queue(1)
        self.__thread = threading.Thread(target = self.run)
        self.__thread.setDaemon(True)

    # PROFETA context
    def start(self):
        self.__sensor.start()
        self.__thread.start()

    def sense(self):
        try:
            e = self.__queue.get_nowait()
            return e
        except Queue.Empty:
            return None

    # sensor context
    def run(self):
        while True:
            e = self.__sensor.sense()
            #print e
            if e is not None:
                self.__queue.put(e)

