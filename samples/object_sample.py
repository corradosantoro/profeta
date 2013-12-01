

import sys
sys.path.append("../lib")

from profeta.lib  import *
from profeta.main import *

class object_at(Reactor):
    pass

class object_got(SingletonBelief):
    pass

class move_to(Action):
    def execute(self):
        x = self[0]
        y = self[1]
        # ... perform movement to x,y
        print "Go to ", x, y


class pick_object(Action):
    def execute(self):
        print "Arm driven"
        # drive the arm to pick object


class show_kb(Action):
    def execute(self):
        print PROFETA.kb()

PROFETA.start()

+object_at("X", "Y") / object_got("no") >> [ move_to("X", "Y"), pick_object(), +object_got("yes"), show_kb() ]

PROFETA.assert_belief(object_got("no"))
PROFETA.assert_belief(object_at(20, 30))
PROFETA.run()
