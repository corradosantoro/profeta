#!/usr/local/bin/python2.6
#
#

import sys
sys.path.append ("../lib")

import time

from profeta.variable  import *
from profeta.attitude  import *
from profeta.inference  import *
from profeta.action  import *
from profeta.lib  import *
from profeta.main import *
from profeta.clepta.sensor  import *


# ------------------------------------------------------------------------------
# {{{ The Beliefs
# ------------------------------------------------------------------------------
class bel(Belief):
    pass

# ------------------------------------------------------------------------------
# }}}
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# {{{ The Goals
# ------------------------------------------------------------------------------

class g1(Goal):
    pass

# ------------------------------------------------------------------------------
# }}}
# ------------------------------------------------------------------------------



def strategy():
    +start() >> [ show_line("1"), +bel("one"), g1(), show_line("3") ]

    g1() >> [ +bel("two"), show_line("2") ]

    +bel("one") >> [ show_line("4"), -bel("one") ]
    +bel("two") >> [ show_line("5"), -bel("two") ]





if __name__ == "__main__":

    PROFETA.start()
    PROFETA.assert_belief(start())

    strategy()

    PROFETA.run_shell(globals())

