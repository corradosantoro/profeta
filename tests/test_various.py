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
class color(Belief):
    pass

class phrase(Belief):
    pass

# ------------------------------------------------------------------------------
# }}}



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
        e = raw_input ("Enter Phrase: ")
        return phrase(e)



def strategy():
    +start() >> [ show("ciao!") ]
    +phrase("one") >> [ show("one"), -phrase("one") ]
    +phrase("X") >> [ show("X"), -phrase("X") ]





if __name__ == "__main__":

    PROFETA.start()
    PROFETA.add_sensor(KB())
    PROFETA.assert_belief(start())

    strategy()

    PROFETA.run()

