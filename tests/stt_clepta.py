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
    +start() >> [ show("ciao!"), say("ciao")  ]
    +hear("ciao") >> [ say("ciao anche a te!"), -hear("ciao") ]
    +hear("come stai") >> [ say("abbastanza bene, e tu?"), -hear("come stai") ]
    +hear("ottimamente") >> [ say("bene, sono contenta per te"), -hear("ottimamente") ]
    +hear("bene") >> [ say("sono contenta per te"), -hear("bene") ]
    +hear("benissimo") >> [ say("bene, sono contenta per te"), -hear("benissimo") ]
    #+hear("X") >> [ show("X"), say("non credo di avere capito"), -hear("X") ]





if __name__ == "__main__":

    PROFETA.start()
    PROFETA.assert_belief(start())

    PROFETA.add_sensor(AsyncSensorProxy(Hearer(threshold=3000, lang='it')))

    say().set_language('it')

    strategy()

    PROFETA.run()

