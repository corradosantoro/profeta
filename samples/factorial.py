#!/usr/local/bin/python2.6
#
#

#import sys
#sys.path.append ("../lib")

from profeta.lib  import *
from profeta.main import *


class fact(Reactor):
    pass

def factorial():
    +fact("N") >> [ +fact("N", 1) ]
    +fact(1, "X") >> [ show("the resulting factorial is "), show_line("X") ]
    +fact("N", "X") >> [ "Y = int(N) * int(X)", "N = int(N) - 1", +fact("N", "Y") ]


if __name__ == "__main__":

    PROFETA.start()

    factorial()

    print "Enter +fact(N) to calculate the factorial of N"

    PROFETA.run_shell(globals())

