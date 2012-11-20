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

global start_time

# ------------------------------------------------------------------------------
# {{{ The Beliefs
# ------------------------------------------------------------------------------
class bel1(Belief):
    pass

class bel2(Belief):
    pass

class bel3(Belief):
    pass

class bel4(Belief):
    pass

class bel5(Belief):
    pass

class bel6(Belief):
    pass

class bel7(Belief):
    pass

class bel8(Belief):
    pass

class bel9(Belief):
    pass

class bel10(Belief):
    pass

class bel11(Belief):
    pass

class bel12(Belief):
    pass

class bel13(Belief):
    pass

class bel14(Belief):
    pass

class bel15(Belief):
    pass

class bel16(Belief):
    pass

class bel17(Belief):
    pass

class bel18(Belief):
    pass

class bel19(Belief):
    pass

class bel20(Belief):
    pass



class bel00(Belief):
    pass


class r(Reactor):
    pass

# ------------------------------------------------------------------------------
# }}}



# ------------------------------------------------------------------------------
# {{{ The Goals
# ------------------------------------------------------------------------------
class goal1(Goal):
    pass

class goal2(Goal):
    pass

class goal3(Goal):
    pass

class goal4(Goal):
    pass

class goal5(Goal):
    pass

class goal6(Goal):
    pass

class goal7(Goal):
    pass

class goal8(Goal):
    pass

class goal9(Goal):
    pass

class goal10(Goal):
    pass

# ------------------------------------------------------------------------------
# }}}




# ------------------------------------------------------------------------------
# {{{ The Actions
# ------------------------------------------------------------------------------
class show(Action):

    def execute(self):
        global start_time
        __str = self[0]
        print time.time() - start_time, __str

# ------------------------------------------------------------------------------
# }}}


def test1():

    ( +goal1() ) >> [ show("Goal 1") ]
    ( +goal2() ) >> [ show("Goal 2") ]
    ( +goal3() ) >> [ show("Goal 3") ]
    ( +goal4() ) >> [ show("Goal 4") ]
    ( +goal5() ) >> [ show("Goal 5") ]
    ( +goal6() ) >> [ show("Goal 6") ]
    ( +goal7() ) >> [ show("Goal 7") ]
    ( +goal8() ) >> [ show("Goal 8") ]
    ( +goal9() ) >> [ show("Goal 9") ]
    ( +goal10() ) >> [ show("Goal 10") ]

    while True:
        for event in [ goal1(), goal2(), goal3(), goal4(), goal5(), goal6(), goal7(), goal8(), goal9(), goal10() ]:
            global start_time
            start_time = time.time()
            Engine.instance().generate_external_event ( +event )
            time.sleep(1)


def test2():

    ( +bel1() ) >> [ show("Bel 1"), -bel1(), +bel00(), -bel00() ]
    ( +bel2() ) >> [ show("Bel 2"), -bel2(), +bel00(), -bel00() ]
    ( +bel3() ) >> [ show("Bel 3"), -bel3(), +bel00(), -bel00() ]
    ( +bel4() ) >> [ show("Bel 4"), -bel4(), +bel00(), -bel00() ]
    ( +bel5() ) >> [ show("Bel 5"), -bel5(), +bel00(), -bel00() ]
    ( +bel6() ) >> [ show("Bel 6"), -bel6(), +bel00(), -bel00() ]
    ( +bel7() ) >> [ show("Bel 7"), -bel7(), +bel00(), -bel00() ]
    ( +bel8() ) >> [ show("Bel 8"), -bel8(), +bel00(), -bel00() ]
    ( +bel9() ) >> [ show("Bel 9"), -bel9(), +bel00(), -bel00() ]
    ( +bel10() ) >> [ show("Bel 10"), -bel10(), +bel00(), -bel00() ]

    ( +bel11() ) >> [ show("Bel 11"), -bel11(), +bel00(), -bel00() ]
    ( +bel12() ) >> [ show("Bel 12"), -bel12(), +bel00(), -bel00() ]
    ( +bel13() ) >> [ show("Bel 13"), -bel13(), +bel00(), -bel00() ]
    ( +bel14() ) >> [ show("Bel 14"), -bel14(), +bel00(), -bel00() ]
    ( +bel15() ) >> [ show("Bel 15"), -bel15(), +bel00(), -bel00() ]
    ( +bel16() ) >> [ show("Bel 16"), -bel16(), +bel00(), -bel00() ]
    ( +bel17() ) >> [ show("Bel 17"), -bel17(), +bel00(), -bel00() ]
    ( +bel18() ) >> [ show("Bel 18"), -bel18(), +bel00(), -bel00() ]
    ( +bel19() ) >> [ show("Bel 19"), -bel19(), +bel00(), -bel00() ]
    ( +bel20() ) >> [ show("Bel 20"), -bel20(), +bel00(), -bel00() ]
    ( +r() ) >> [ show("Reactor"), +bel00(), -bel00() ]

    if True:
        ( +goal1() ) >> [ show("Goal 1") ]
        ( +goal2() ) >> [ show("Goal 2") ]
        ( +goal3() ) >> [ show("Goal 3") ]
        ( +goal4() ) >> [ show("Goal 4") ]
        ( +goal5() ) >> [ show("Goal 5") ]
        ( +goal6() ) >> [ show("Goal 6") ]
        ( +goal7() ) >> [ show("Goal 7") ]
        ( +goal8() ) >> [ show("Goal 8") ]
        ( +goal9() ) >> [ show("Goal 9") ]
        ( +goal10() ) >> [ show("Goal 10") ]

    while True:
        for event in [ bel1(), bel10() , r() ]:#, bel20() ]:
            global start_time
            start_time = time.time()
            Engine.instance().generate_external_event ( +event )
            time.sleep(0.3)
        print ""






if __name__ == "__main__":

    CreateEngine()
    Engine.instance().set_debug (False)
    ex = ThreadedEngineExecutor (Engine.instance())
    ex.start ()

    test2()

