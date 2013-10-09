#
# action.py
#

import threading
import Queue

from profeta.action import *

class AsyncActionExecutor(threading.Thread):

    def __init__(self, uService):
        threading.Thread.__init__(self)
        self.setDaemon(False)
        self.__service = uService
        self.__queue = Queue.Queue(1)

    def get_service(self):
        return self.__service

    def async_invoke(self, uData):
        self.__queue.put(uData)

    def run(self):
        while True:
            (uMethod, uArgs) = self.__queue.get()
            apply (uMethod, uArgs)



class AsyncActionMap:

    EXECUTORS = {}

    @classmethod
    def bind(cls, uActionObject):
        action_class = uActionObject.__class__.__name__
        if cls.EXECUTORS.has_key(action_class):
            return
        else:
            service = uActionObject.create_service()
            thr = AsyncActionExecutor(service)
            cls.EXECUTORS[action_class] = thr
            thr.start()

    @classmethod
    def get_service(cls, uActionObject):
        thr = cls.EXECUTORS[uActionObject.__class__.__name__]
        return thr.get_service()

    @classmethod
    def async_invoke(cls, uActionObject, uData):
        thr = cls.EXECUTORS[uActionObject.__class__.__name__]
        thr.async_invoke(uData)


class AsyncAction(Action):

    def __init__(self, *args, **kwargs):
        apply (Action.__init__, (self,) + args)
        self.bind()

    def create_service(self):
        raise "Needs to be overridden"

    def bind(self):
        AsyncActionMap.bind(self)

    def get_service(self):
        return AsyncActionMap.get_service(self)

    def async_invoke(self, uMethod, uArgs):
        AsyncActionMap.async_invoke(self, (uMethod, uArgs) )

