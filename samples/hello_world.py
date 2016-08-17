#!/usr/local/bin/python2.6

from profeta.lib  import *
from profeta.main import *

# a "say" belief
class say(Belief): pass

PROFETA.start()  # instantiate the engine

# define a rule: when you say "hi", PROFETA answers "hello world"
+say("hi") >> [ show_line("'Hello world' from PROFETA") ]

PROFETA.run_shell(globals())

