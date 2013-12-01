#!/usr/local/bin/python2.6
#
#

import sys
sys.path.append ("../lib")

from profeta.lib  import *
from profeta.main import *


class do_factorial(Reactor):
    pass

class fact(Goal):
    pass

class KB(Sensor):
    def sense(self):
        e = raw_input ("Enter Number: ")
        return +do_factorial(int(e))


def factorial():
    +do_factorial("N") >> [ show("computing factorial of "), show_line("N"), fact("N", 1) ]
    fact(1, "X") >> [ show("the resuilting factorial is "), show_line("X") ]
    fact("N", "X") >> [ "Y = int(N) * int(X)", "N = int(N) - 1", fact("N", "Y") ]



if __name__ == "__main__":

    PROFETA.start()
    PROFETA.add_sensor(KB())

    factorial()

    PROFETA.run()

