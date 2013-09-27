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
        cls.__thread.start ()

    @classmethod
    def kb(cls):
        return cls.__engine.kb()

    @classmethod
    def event(cls, evt):
        cls.__engine.generate_external_event(evt)


