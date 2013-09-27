#!/usr/local/bin/python2.6
#
#

import sys
sys.path.append ("../lib")

import time

from profeta.attitude  import *
from profeta.inference  import *
from profeta.action  import *
from profeta.lib  import *
from profeta.main import *

_ = v


# ------------------------------------------------------------------------------
# {{{ The Reactors
# ------------------------------------------------------------------------------
class target_got(Reactor):
    pass

class king_got(Reactor):
    pass

class queen_got(Reactor):
    pass

class go(Reactor):
    pass

# ------------------------------------------------------------------------------
# {{{ The Beliefs
# ------------------------------------------------------------------------------
class color(Belief):
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
class exit_from_area_path(Action):

    def execute(self):
        print self.__class__.__name__


# ------------------------------------------------------------------------------
class first_row_path(Action):

    def execute(self):
        print self.__class__.__name__ + ":" + repr(self[0])


# ------------------------------------------------------------------------------
class from_first_to_second_row_path(Action):

    def execute(self):
        print self.__class__.__name__


# ------------------------------------------------------------------------------
class second_row_path(Action):

    def execute(self):
        print self.__class__.__name__


# ------------------------------------------------------------------------------
class activate_left_scanner(Action):

    def execute(self):
        print self.__class__.__name__


# ------------------------------------------------------------------------------
class activate_right_scanner(Action):

    def execute(self):
        print self.__class__.__name__


# ------------------------------------------------------------------------------
class stop_scanner(Action):

    def execute(self):
        print self.__class__.__name__


# ------------------------------------------------------------------------------
class activate_left_arm_automation(Action):

    def execute(self):
        print self.__class__.__name__


# ------------------------------------------------------------------------------
class activate_right_arm_automation(Action):

    def execute(self):
        print self.__class__.__name__


# ------------------------------------------------------------------------------
class save_king_position(Action):

    def execute(self):
        print self.__class__.__name__


# ------------------------------------------------------------------------------
class save_queen_position(Action):

    def execute(self):
        print self.__class__.__name__


# ------------------------------------------------------------------------------
# }}}


def strategy():


    goal("main")
    +start() >> [ start_goal("exit_from_area") ]


    goal("exit_from_area")
    +start() / color("C") >> [ exit_from_area_path("C") ]
    +target_got() / color("red") >> [ activate_right_arm_automation(),
                                      activate_left_scanner(),
                                      start_goal("first_row") ]
    +target_got() / color("blue") >> [ activate_left_arm_automation(),
                                       activate_right_scanner(),
                                       start_goal("first_row") ]


    goal("first_row")
    +start() / color("C") >> [ first_row_path("C") ]
    +king_got()   >> [ save_king_position() ]
    +queen_got()  >> [ save_queen_position () ]
    +target_got() >> [ start_goal("from_first_to_second_row") ]


    goal("from_first_to_second_row")
    +start() / color("C") >> [ stop_scanner(),
                               from_first_to_second_row_path("C") ]
    +target_got() / color("red") >> [ activate_left_arm_automation(),
                                      start_goal("second_row") ]
    +target_got() / color("blue") >> [ activate_right_arm_automation(),
                                       start_goal("second_row") ]


    goal("second_row")
    +start() / color("C") >> [ second_row_path("C") ]
    +target_got() >> [ show("###END###") ]






if __name__ == "__main__":

    PROFETA.start()

    strategy()

    while True:
        print "\nNew KB is : ", Engine.kb()
        e = input ("Belief: ")
        PROFETA.event ( +e )
        time.sleep (1)

