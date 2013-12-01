#
#
#

from profeta.attitude  import *
from profeta.inference  import *
from profeta.action  import *
from profeta.lib  import *
from profeta.threaded_engine_executor import *

class PROFETA:

    __thread = None
    __engine = None
    __ticks = None
    __is_running = True

    @classmethod
    def start(cls, ticks = 0, debug = False ):
        cls.__is_running = True
        cls.__engine = CreateEngine(ticks)
        cls.__engine.set_debug (debug)
        cls.__ticks = ticks / 1000.0
        #cls.__thread = ThreadedEngineExecutor (Engine.instance())
        #cls.__thread.start ()

    @classmethod
    def stop(cls):
        cls.__is_running = False

    @classmethod
    def run(cls):
        while cls.__is_running:
            cls.__engine.execute()
            time.sleep(cls.__ticks)

    @classmethod
    def kb(cls):
        return cls.__engine.kb()

    @classmethod
    def assert_belief(cls, b):
        if isinstance(b, Belief):
            cls.__engine.generate_external_event(+b)
        else:
            raise "Not a belief or reactor"

    @classmethod
    def achieve(cls, g):
        if isinstance(g, Goal):
            cls.__engine.generate_external_event(+g)
        else:
            raise "Not a Goal"

    @classmethod
    def add_sensor(cls, sensor):
        cls.__engine.add_event_poller(sensor)

    @classmethod
    def set_current_episode(cls, ep):
        cls.__engine.set_current_episode(ep)


