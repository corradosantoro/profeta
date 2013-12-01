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



# ------------------------------------------------------------------------------
# {{{ The Actions
# ------------------------------------------------------------------------------
class show(Action):

    def execute(self):
        print self[0]

# ------------------------------------------------------------------------------
# }}}

class KB(Sensor):

    def sense(self):
        print "KB is:", PROFETA.kb()
        e = raw_input ("Enter Phrase: ")
        if e == "stop":
            PROFETA.stop()
            return None
        else:
            return (+ phrase(e))



def strategy():
    +start() >> [ show("ciao!") ]
    +phrase("one") >> [ show("the triggered rule is one"), -phrase("one"), g1(),g2() ]
    +phrase("ciao") >> [ show("ciao ciao!") ]
    +phrase("X") / (lambda : (int(X) > 20)) >> [ show("rule X > 20"), "Y = int(X) - 1", show("Y"), -phrase("X") ]
    +phrase("X") >> [ fact("X"), -phrase("X") ]

    g1() >> [ show("this is the goal 'G1'"), +phrase("ciao") ]
    g2() >> [ show("this is the goal 'G2'") ]

    fact("X") >> [ fact("X", 1) ]
    fact("X", "N") / (lambda : int(X) == 0) >> [ show("N") ]
    fact("X", "N") >> [ "N1 = int(N) * int(X)", "X1 = int(X) - 1", fact("X1", "N1") ]






if __name__ == "__main__":

    PROFETA.start()
    PROFETA.add_sensor(AsyncSensorProxy(KB()))
    PROFETA.assert_belief(start())

    strategy()

    PROFETA.run()

