#
#
#

import threading
import sys

from profeta.attitude  import *
from profeta.inference  import *
from profeta.action  import *
from profeta.lib  import *
from profeta.threaded_engine_executor import *

class PROFETA:

    __thread = None
    __engine = None
    __is_running = True

    @classmethod
    def start(cls, ticks = 0, debug = False ):
        cls.__is_running = True
        cls.__engine = CreateEngine(ticks)
        cls.__engine.set_debug (debug)

    @classmethod
    def set_debug(cls, debug):
        cls.__engine.set_debug(debug)

    @classmethod
    def stop(cls):
        cls.__engine.put_top_event(None)
        cls.__is_running = False

    @classmethod
    def run(cls):
        while cls.__is_running:
            cls.__engine.execute()

    @classmethod
    def run_shell(cls, g):
        sh = SHELL(g)
        sh.start()
        while cls.__is_running:
            cls.__engine.execute()

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
    def retract_belief(cls, b):
        if isinstance(b, Belief):
            cls.__engine.generate_external_event(-b)
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



class SHELL(threading.Thread):

    def __init__(self, glob):
        threading.Thread.__init__ (self)
        self.__globals = glob
        self.setDaemon(True)

    def run(self):
        while True:
            s = raw_input("PROFETA>").strip()
            if s == "":
                continue
            if s[0] == '+':
                s = "assert " + s[1:]
            if s[0] == '-':
                s = "retract " + s[1:]
            if s[0] == '~':
                s = "achieve " + s[1:]
            args = s.split()
            cmd = "C_" + args[0]
            if not(hasattr(self,cmd)):
                print "Invalid command"
                continue
            getattr(self, cmd)(args[1:])


    def C_help(self, args):
        print "assert B           asserts a belief"
        print "+B                 asserts a belief"
        print "retract B          retract a belief"
        print "-B                 retract a belief"
        print "achieve G          achieves a goal"
        print "~G                 achieves a goal"
        print "kb                 prints the knowledge base"
        print "verbose on|off     sets the verbosity on or off"
        print "help               shows help"
        print "quit               quits PROFETA"


    def C_kb(self, args):
        print PROFETA.kb()


    def C_quit(self, args):
        PROFETA.stop()
        sys.exit(0)


    def C_assert(self, args):
        if len(args) == 0:
            print "assert: missing belief"
            return
        try:
            B = eval(args[0], self.__globals)
            PROFETA.assert_belief(B)
        except:
            print "Unexpected error in ASSERT:", sys.exc_info()[0]


    def C_retract(self, args):
        if len(args) == 0:
            print "retract: missing belief"
            return
        try:
            B = eval(args[0], self.__globals)
            PROFETA.retract_belief(B)
        except:
            print "Unexpected error in RETRACT:", sys.exc_info()[0]


    def C_achieve(self, args):
        if len(args) == 0:
            print "achieve: missing goal"
            return
        try:
            G = eval(args[0], self.__globals)
            PROFETA.achieve(G)
        except:
            print "Unexpected error in ACHIEVE:", sys.exc_info()[0]


    def C_verbose(self, args):
        if len(args) == 0:
            print "verbose: missing parameter"
            return
        if args[0] == "on":
            PROFETA.set_debug(True)
        elif args[0] == "off":
            PROFETA.set_debug(False)
        else:
            print "verbose: invalid parameter"
