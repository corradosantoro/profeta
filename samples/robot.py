#
#
#

import math


class FixedObject:

    def __init__(self, uPosition, uRadius):
        self.__position = uPosition
        self.__radius = uRadius
        self.__environment = None

    def set_environment(self, uE):
        self.__environment = uE

    def get_environment(self):
        return self.__environment

    def get_position(self):
        return self.__position

    def set_position(self, uP):
        self.__position = uP

    def get_radius(self):
        return self.__radius

    def collide(self, uOtherobject):
        p1 = self.__position
        p2 = uOtherobject.get_position()
        d = math.hypot(p1[0] - p2[0], p1[1] - p2[1])
        r = (self.__radius + uOtherobject.get_radius())
        #print "COLLISION CHECK ", p1, p2, d, r, d<=r
        return d <= r

    def distance_from(self, position):
        p1 = self.__position
        p2 = position
        return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

    def normalize_angle(self, uA):
        while uA > 180:
            uA = uA - 360
        while uA < -180:
            uA = uA + 360
        return uA


class MovableObject(FixedObject):

    def __init__(self, uPosition, uRadius, uTheta = 0):
        FixedObject.__init__(self, uPosition, uRadius)
        self.__theta = uTheta
        self.__v_speed = 0
        self.__w_speed = 0
        self.__collision = False

    def get_theta(self):
        return self.__theta

    def set_theta(self, uT):
        self.__theta = self.normalize_angle(uT)

    def get_collision(self):
        return self.__collision

    def set_v_speed(self, uSpeed):
        self.__v_speed = uSpeed

    def set_w_speed(self, uSpeed):
        self.__w_speed = uSpeed

    def move(self):
        self.__theta += self.__w_speed
        self.__theta = self.normalize_angle(self.__theta)
        dx = self.__v_speed * math.cos(math.radians(self.__theta))
        dy = self.__v_speed * math.sin(math.radians(self.__theta))
        old_p = self.get_position()
        new_p = (old_p[0] + dx, old_p[1] + dy)
        #print self, "POS = (old, new)", self.get_position(), p
        self.set_position(new_p)
        if self.get_environment().border_collide(self):
            self.__collision = True
        else:
            if self.get_environment().collide(self) == []:
                self.__collision = False
            else:
                self.__collision = True

        if self.__collision:
            self.set_position(old_p)

        return not(self.__collision)



class Environment:

    def __init__(self, uSize):
        self.__size = uSize
        self.__movable_objects = []
        self.__fixed_objects = []

    def add_fixed_object(self, uObj):
        uObj.set_environment(self)
        self.__fixed_objects.append(uObj)

    def add_movable_object(self, uObj):
        uObj.set_environment(self)
        self.__movable_objects.append(uObj)

    def add_robot(self, uR):
        self.add_movable_object(uR)

    def get_robot(self):
        return self.__movable_objects[0]

    def border_collide(self, uObj):
        p = uObj.get_position()
        r = uObj.get_radius()
        if ((p[0] - r) < 0) or ((p[1] - r) < 0) or \
           ((p[0] + r) > self.__size[0]) or ((p[1] + r) > self.__size[1]):
            return True
        else:
            return False


    def collide(self, uObj):
        collision_list = []
        for o in self.__fixed_objects + self.__movable_objects:
            if o != uObj:
                if uObj.collide(o):
                    collision_list.append(o)
        return collision_list

    def step(self):
        for obj in self.__movable_objects:
            obj.move()



class Robot(MovableObject):

    def __init__(self, uPosition, uRadius, uTheta = 0):
        MovableObject.__init__(self, uPosition, uRadius, uTheta)
        self.__target_got = False
        self.__target = None
        self.__target_method = None
        self.__rot_speed = 0
        self.__lin_speed = 0
        self.__command_queue = []


    def set_rotation_speed(self, u):
        self.__rot_speed = u


    def set_linear_speed(self, v):
        self.__lin_speed = v


    def get_target_got(self):
        return self.__target_got

    def clear_target_got(self):
        self.__target_got = False

    def stop(self):
        self.__command_queue = []
        self.set_w_speed(0)
        self.set_v_speed(0)

    def rotate_absolute(self, uDegrees):
        self.__command_queue.append ( (self.check_target_angle, uDegrees) )


    def rotate_relative(self, uDegrees):
        self.__command_queue.append ( (self.init_relative_rotation, uDegrees) )
        self.__command_queue.append ( (self.check_target_relative_angle, uDegrees) )


    def forward_to_distance(self, uDistance):
        self.__command_queue.append ( (self.init_distance, uDistance) )
        self.__command_queue.append ( (self.check_distance, uDistance) )


    def forward_to_point(self, uX, uY):
        self.__command_queue.append ( (self.init_rotation_point, (uX, uY)) )
        self.__command_queue.append ( (self.check_target_relative_angle, 0) )
        self.__command_queue.append ( (self.init_distance_point, (uX, uY)) )
        self.__command_queue.append ( (self.check_distance, 0) )

    def move(self):
        MovableObject.move(self)
        if self.__command_queue != []:
            self.__target_got = False
            (meth, target) = self.__command_queue[0]
            if meth(target):
                self.__command_queue = self.__command_queue[1:]
                if self.__command_queue == []:
                    self.__target_got = True


    def check_target_angle(self, target):
        diff = target - self.get_theta()
        if abs(diff) < 2:  # 2 degrees
            self.set_w_speed(0)
            self.set_v_speed(0)
            self.set_theta(target)
            return True
        else:
            if diff > 0:
                self.set_w_speed(self.__rot_speed)
            else:
                self.set_w_speed(-self.__rot_speed)
            return False


    def init_distance(self, uDistance):
        self.__starting_position = self.get_position()
        (x, y) = self.__starting_position
        x += uDistance * math.cos(math.radians(self.get_theta()))
        y += uDistance * math.sin(math.radians(self.get_theta()))
        self.__target_position = (x, y)
        return True

    def check_distance(self, targetDistance):
        if targetDistance < 0:
            sign = -1
        else:
            sign = 1
        targetDistance = abs(targetDistance)
        diff = targetDistance - self.distance_from(self.__starting_position)
        if abs(diff) < 20: # 2cm
            self.set_w_speed(0)
            self.set_v_speed(0)
            self.set_position(self.__target_position)
            return True
        else:
            if sign*diff > 0:
                self.set_v_speed(self.__lin_speed)
            else:
                self.set_v_speed(-self.__lin_speed)
            return False

    def init_relative_rotation(self, uTarget):
        self.__target_angle = self.normalize_angle(self.get_theta() + uTarget)
        return True

    def check_target_relative_angle(self, uTarget):
        return self.check_target_angle(self.__target_angle)

    def init_rotation_point(self, uPos):
        (uX, uY) = uPos
        self.__starting_position = self.get_position()
        (x, y) = self.__starting_position
        point_heading = math.degrees(math.atan2(uY - y, uX - x))
        self.__target_angle = self.normalize_angle(point_heading - self.get_theta())
        return True

    def init_distance_point(self, uPos):
        (uX, uY) = uPos
        self.__starting_position = self.get_position()
        (x, y) = self.__starting_position
        distance = math.hypot(y - uY, x - uX)
        (meth, param) = self.__command_queue[1]
        self.__command_queue[1] = (meth, distance)
        self.__target_position = (uX, uY)
        return True


