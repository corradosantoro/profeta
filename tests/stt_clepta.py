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
from profeta.clepta.google import *





# ------------------------------------------------------------------------------
# {{{ The Actions
# ------------------------------------------------------------------------------
class show(Action):

    def execute(self):
        print self[0]



def strategy():
    +start() >> [ show("ciao!"), say("ciao, dimmi qualcosa")  ]
    +hear("X") >> [ show("X"), say("hai detto"), say("X"), -hear("X") ]





if __name__ == "__main__":

    PROFETA.start()
    PROFETA.assert_belief(start())

    h = Hearer(threshold=240)
    sp = AsyncSensorProxy(h)
    PROFETA.add_sensor(sp)

    h.set_language('it')


    say().set_language('it')

    strategy()

    PROFETA.run()

