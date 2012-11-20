#!/usr/local/bin/python2.6
#
#

import sys
sys.path.append ("../lib")

import time

from profeta.attitude  import *
from profeta.inference  import *
from profeta.action  import *
from profeta.threaded_engine_executor import *

_ = v


# ------------------------------------------------------------------------------
# {{{ The Beliefs
# ------------------------------------------------------------------------------
class object_seen(Belief):
    pass

class arm_deployed(Belief):
    pass

# ------------------------------------------------------------------------------
# }}}



# ------------------------------------------------------------------------------
# {{{ The Goals
# ------------------------------------------------------------------------------
class prepare_arm(Goal):
    pass

class reach_object(Goal):
    pass

class pick_object(Goal):
    pass

# ------------------------------------------------------------------------------
# }}}




# ------------------------------------------------------------------------------
# {{{ The Actions
# ------------------------------------------------------------------------------
class show(Action):

    def execute(self):
        __str = self[0]
        print __str

# ------------------------------------------------------------------------------
class retract_arm(Action):

    def execute(self):
        print "1- Retracting arm", self[0]


# ------------------------------------------------------------------------------
class deploy_arm(Action):

    def execute(self):
        print "2- Deploying arm", self[0]


# ------------------------------------------------------------------------------
class orientate_towards(Action):

    def execute(self):
        print "3- Orientating towards: ", self[0], self[1]


# ------------------------------------------------------------------------------
class go_to(Action):

    def execute(self):
        print "4- Going towards: ", self[0], self[1]


# ------------------------------------------------------------------------------
class activate_arm(Action):

    def execute(self):
        print "5- Activating arm", self[0]
        print ""

# ------------------------------------------------------------------------------
# }}}


def strategy():

    ( +object_seen("Type", "X", "Y") ) >> [ +~prepare_arm("Type"),
                                            +~reach_object("X", "Y"),
                                            +~pick_object("Type"),
                                            -object_seen("Type", "X", "Y") ]

    ( +~prepare_arm("ball") | (arm_deployed("cylinder"))) >> [ retract_arm("cylinder"),
                                                               -arm_deployed("cylinder"),
                                                               deploy_arm("ball"),
                                                               +arm_deployed("ball") ]

    ( +~prepare_arm("cylinder") | arm_deployed("ball")) >> [ retract_arm("ball"),
                                                             -arm_deployed("ball"),
                                                             deploy_arm("cylinder"),
                                                             +arm_deployed("cylinder") ]

    ( +~prepare_arm("X") | arm_deployed("X") ) >> [ show ("") ]

    ( +~reach_object("X","Y") ) >> [ orientate_towards("X","Y"),
                                     go_to("X","Y") ]

    ( +~pick_object("X") ) >> [ activate_arm("X") ]




if __name__ == "__main__":

    CreateEngine()
    Engine.instance().set_debug (False)
    ex = ThreadedEngineExecutor (Engine.instance())
    ex.start ()

    #(+the_event()) >> [ the_action() ] #, -the_event() ]

    strategy()
    Engine.instance().generate_external_event ( [ +arm_deployed("ball") ])

    while True:
        print "\nNew KB is : ", Engine.kb()
        n = input ("how many objects ? ")
        l = []
        for i in range(0,n):
            print "\n*** OBJECT ", i+1, " ***"
            a = raw_input("(b)all or (c)ylinder? ")
            if a == "b":
                Type = "ball"
            else:
                Type = "cylinder"

            (X, Y) = input("position (x,y) ? ")
            l.append (+object_seen(Type, X, Y))

        print ""
        print "Events generated ", l
        print "Current KB: ", Engine.kb()

        Engine.instance().generate_external_event ( l )

        time.sleep (2)

