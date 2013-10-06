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

    @classmethod
    def start(cls, ticks = 10, debug = False ):
        cls.__engine = CreateEngine(ticks)
        cls.__engine.set_debug (debug)
        cls.__thread = ThreadedEngineExecutor (Engine.instance())
        #cls.__thread.start ()

    @classmethod
    def run(cls):
        cls.__thread.run()

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
    def add_sensor(cls, sensor):
        cls.__engine.add_event_poller(sensor)

    @classmethod
    def set_current_episode(cls, ep):
        cls.__engine.set_current_episode(ep)


