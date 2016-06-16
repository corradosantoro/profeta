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


# ------------------------------------------------------------------------------
# {{{ The Beliefs
# ------------------------------------------------------------------------------
class phrase(Belief):
    pass

class fact_result(Belief):
    pass

# ------------------------------------------------------------------------------
# }}}


class fact(Goal):
    pass


class g1(Goal):
    pass


class g2(Goal):
    pass


class g3(Goal):
    pass



# ------------------------------------------------------------------------------
# {{{ The Actions
# ------------------------------------------------------------------------------
class show(Action):

    def execute(self):
        print self[0]


class failure_action(Action):

    def execute(self):
        fail().execute()

# ------------------------------------------------------------------------------
# }}}



def strategy():
    +start() >> [ show_line("ciao!"), g1("call"), show_line("end") ]

    g1("call") >> [ show_line("this is the goal 'G1'"), g2(), show_line("after calling 'g2'") ]
    g1("_") >> [ show_line("this is the goal 'G1'") ]
    g2() >> [ show_line("this is the goal 'G2'"), g3(), show_line("after calling 'g3'") ]
    g3() >> [ show_line("this is the goal 'G3'") , failure_action() ]

    -g3() >> [ show_line("plan G3 failed"), fail() ]
    -g2() >> [ show_line("plan G2 failed"), fail() ]
    -g1("_") >> [ show_line("plan G1 failed"), fail() ]





if __name__ == "__main__":

    PROFETA.start()
    PROFETA.assert_belief(start())

    strategy()

    PROFETA.run_shell(globals())

