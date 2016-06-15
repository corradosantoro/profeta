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


class g1(Goal):
    pass


# ------------------------------------------------------------------------------
# {{{ The Actions
# ------------------------------------------------------------------------------

class failure_action(Action):

    def execute(self):
        fail().execute()

# ------------------------------------------------------------------------------
# }}}



def strategy():
    +start() >> [ show_line("ciao!"), +bel("one"), g1(), show_line("end of start plan") ]

    g1() >> [ +bel("two"), show_line("this is the goal 'G1'") ]

    +bel("one") >> [ show_line("after bel one"), -bel("one") ]
    +bel("two") >> [ show_line("after bel two"), -bel("two") ]





if __name__ == "__main__":

    PROFETA.start()
    PROFETA.assert_belief(start())

    strategy()

    PROFETA.run_shell(globals())

