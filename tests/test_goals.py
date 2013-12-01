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
    +start() >> [ show("ciao!"), g1(), show("end") ]

    g1() >> [ show("this is the goal 'G1'"), g2(), show("after calling 'g2'") ]
    g2() >> [ show("this is the goal 'G2'"), g3(), show("after calling 'g3'") ]
    g3() >> [ show("this is the goal 'G3'") , failure_action() ]

    -g3() >> [ show("plan G3 failed"), fail() ]
    -g2() >> [ show("plan G2 failed"), fail() ]
    -g1() >> [ show("plan G1 failed"), fail() ]





if __name__ == "__main__":

    PROFETA.start()
    PROFETA.assert_belief(start())

    strategy()

    PROFETA.run()

