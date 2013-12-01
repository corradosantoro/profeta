#!/usr/local/bin/python2.6
#
#

import sys
sys.path.append ("../lib")

from profeta.lib  import *
from profeta.main import *

PROFETA.start()  # instantiate the engine

# define a rule
+start() >> [ show_line("hello world from PROFETA") ]

# assert the "start()" belief
PROFETA.assert_belief(start())

# run the engine
PROFETA.run()

