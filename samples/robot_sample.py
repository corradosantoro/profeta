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

from robot import *

global ENV

ENV = None


# ------------------------------------------------------------------------------
# {{{ The Beliefs
# ------------------------------------------------------------------------------
class position(SingletonBelief):
    pass

class hexagone_point(SingletonBelief):
    pass


# ------------------------------------------------------------------------------
# {{{ The Reactors
# ------------------------------------------------------------------------------
class target_got(Reactor):
    pass

class collision(Reactor):
    pass

# ------------------------------------------------------------------------------
# {{{ The Goals
# ------------------------------------------------------------------------------
class go(Goal):
    pass

class do_hexagone(Goal):
    pass

# ------------------------------------------------------------------------------
# {{{ The Actions
# ------------------------------------------------------------------------------
class show_robot_position(Action):

    def execute(self):
        p = ENV.get_robot().get_position()
        print "The current position of the robot is ", p


class stop(Action):
    def execute(self):
        ENV.get_robot().stop()


class forward(Action):
    def execute(self):
        ENV.get_robot().forward_to_distance(self[0])


class rotate_to(Action):
    def execute(self):
        ENV.get_robot().rotate_absolute(self[0])


class rotate(Action):
    def execute(self):
        ENV.get_robot().rotate_relative(self[0])


class SimulationStep(Sensor):

    def sense(self):
        ENV.step() # execute one step of simulation
        return None

class TargetSensor(Sensor):

    def sense(self):
        r = ENV.get_robot()
        if r.get_target_got():
            r.clear_target_got()
            return +target_got()
        else:
            return None

class CollisionSensor(Sensor):

    def sense(self):
        r = ENV.get_robot()
        if r.get_collision():
            return +collision()
        else:
            return None

class PositionSensor(Sensor):

    def sense(self):
        ENV.step() # execute one step of simulation
        p = ENV.get_robot().get_position()
        th = ENV.get_robot().get_theta()
        return position(p[0], p[1], th)


# ------------------------------------------------------------------------------
# {{{ The Strategy
# ------------------------------------------------------------------------------
def strategy():
    go() >> [ show_line("starting the robot!"), set_context("first_step") ]

    context("first_step")
    +start() >> [ rotate_to(45), forward(500) ]
    +target_got() >> [ show_robot_position(), set_context("hexagone") ]

    context("hexagone")
    +start() >> [ +hexagone_point(0), do_hexagone() ]
    do_hexagone() / hexagone_point(0) >> [ rotate_to(0), forward(300) ]
    do_hexagone() / hexagone_point(6) >> [ stop() ]
    do_hexagone() / hexagone_point("X") >> [ rotate(60), forward(300) ]
    +target_got() / hexagone_point("N") >> [ show_robot_position(), "N = int(N) + 1", +hexagone_point("N"), do_hexagone() ]


if __name__ == "__main__":

    ENV = Environment( (2000,2000) )
    #ENV.add_fixed_object(FixedObject( (100, 500), 100 ))

    robot = Robot( (100, 100) , 100, 0)
    robot.set_rotation_speed(3.5) # 2 degrees/step
    robot.set_linear_speed(7.3) # 5 mm/step
    ENV.add_robot(robot)

    PROFETA.start()
    PROFETA.add_sensor(SimulationStep())
    PROFETA.add_sensor(TargetSensor())
    PROFETA.add_sensor(CollisionSensor())
    PROFETA.add_sensor(PositionSensor())

    PROFETA.achieve(go())

    strategy()

    PROFETA.run()

