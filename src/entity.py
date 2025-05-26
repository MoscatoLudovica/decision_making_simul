import math, logging
from random import Random
from geometry_utils.vector3D import Vector3D
from bodies.shapes3D import Shape3DFactory
class EntityFactory:
    
    @staticmethod
    def create_entity(entity_type:str,config_elem: dict,_id:int=0):
        check_type = entity_type.split('_')[0]+'_'+entity_type.split('_')[1]
        if check_type == "agent_static":
            return StaticAgent(entity_type,config_elem,_id)
        elif check_type == "agent_movable":
            return MovableAgent(entity_type,config_elem,_id)
        elif check_type == "object_static":
            return StaticObject(entity_type,config_elem,_id)
        elif check_type == "object_movable":
            return MovableObject(entity_type,config_elem,_id)
        else:
            raise ValueError(f"Invalid agent type: {entity_type}")

class Entity:
    def __init__(self,entity_type:str, config_elem: dict,_id:int=0):
        self.entity_type = entity_type
        self._id = _id
        self.position_from_dict = False
        self.orientation_from_dict = False
        self.color = config_elem.get("color","gray")
    
    def get_name(self):
        return self.entity_type+"_"+str(self._id)

    def get_position_from_dict(self):
        return self.position_from_dict
    
    def get_orientation_from_dict(self):
        return self.orientation_from_dict

    def reset(self):
        pass

    def entity(self) -> str:
        return self.entity_type
    
class Object(Entity):    
    def __init__(self,entity_type:str, config_elem: dict,_id:int=0):
        super().__init__(entity_type,config_elem,_id)
        self.color = config_elem.get("color","green")
        if config_elem.get("_id") in ("idle","interactive"):
            self.entity_type += "_"+str(config_elem.get("_id"))
            if config_elem.get("_id") == "idle":
                self.color = config_elem.get("color","black")
        else: raise ValueError(f"Invalid object type: {self.entity_type}")
        logging.info(f"Object {self.entity_type} id {self._id} intialized")

class Agent(Entity):
    def __init__(self,entity_type:str, config_elem: dict,_id:int=0):
        super().__init__(entity_type,config_elem,_id)
        self.random_generator = Random()
        self.ticks_per_second = config_elem.get("ticks_per_second",31)
        self.color = config_elem.get("color","blue")
        logging.info(f"Agent {self.entity_type} id {self._id} intialized")
    
    def ticks(self): return self.ticks_per_second
    
    def set_random_generator(self,random_seed):
        seed = random_seed + int(self._id) + (int(self.entity_type.split('_')[-1]) + 1)
        self.random_generator.seed(seed)

    def get_random_generator(self):
        return self.random_generator

    def run(self,tick,arena_shape):
        pass

class StaticObject(Object):
    def __init__(self,entity_type:str, config_elem:dict,_id:int=0):
        super().__init__(entity_type,config_elem,_id)
        if config_elem.get("shape") in ("circle","square","rectangle"):
            self.entity_type = entity_type + "_"+str(config_elem.get("shape"))
            self.shape_type = "flat"
        elif config_elem.get("shape") in ("sphere","cube","cuboid","cylinder"):
            self.entity_type = entity_type + "_"+str(config_elem.get("shape"))
            self.shape_type = "dense"
        else: raise ValueError(f"Invalid object type: {self.entity_type}")
        self.shape = Shape3DFactory.create_shape("object",config_elem.get("shape","point"), {key:val for key,val in config_elem.items()})
        self.position = Vector3D()
        self.orientation = Vector3D()
        self.start_position = Vector3D()
        self.start_orientation = Vector3D()
        temp_position = config_elem.get("position", None)
        if temp_position != None:
            self.position_from_dict = True
            try:
                self.start_position = Vector3D(temp_position[_id][0],temp_position[_id][1],temp_position[_id][2])
            except:
                self.start_position = Vector3D(temp_position[-1][0],temp_position[-1][1],temp_position[-1][2])
            self.set_start_position(self.start_position)
        temp_orientation = config_elem.get("orientation", None)
        if temp_orientation != None:
            self.orientation_from_dict = True
            try:
                self.start_orientation = Vector3D(temp_orientation[_id][0],temp_orientation[_id][1],temp_orientation[_id][2])
            except:
                self.start_orientation = Vector3D(temp_orientation[-1][0],temp_orientation[-1][1],temp_orientation[-1][2])
            self.orientation = self.start_orientation
            self.set_start_orientation(self.start_orientation)

    def to_origin(self):
        self.position = Vector3D()
        self.orientation = Vector3D()
        self.shape.center = self.position
        self.shape.set_vertices()

    def set_start_position(self,new_position:Vector3D,_translate:bool = True):
        self.start_position = new_position
        self.set_position(new_position,_translate)

    def set_position(self,new_position:Vector3D,_translate:bool = True):
        self.position = new_position
        if _translate: self.shape.translate(self.position)

    def set_start_orientation(self,new_orientation:Vector3D):
        self.start_orientation = new_orientation
        self.set_orientation(new_orientation)

    def set_orientation(self,new_orientation:Vector3D):
        self.orientation = new_orientation
        self.shape.rotate(self.start_orientation.z)

    def get_start_position(self):
        return self.start_position
    
    def get_start_orientation(self):
        return self.start_orientation
    
    def get_position(self):
        return self.position

    def get_orientation(self):
        return self.orientation
        
    def close(self):
        del self.shape

    def get_shape(self):
        return self.shape

    def get_shape_type(self):
        return self.shape_type
    
class StaticAgent(Agent):
    def __init__(self,entity_type:str, config_elem:dict,_id:int=0):
        super().__init__(entity_type,config_elem,_id)
        if config_elem.get("shape") in ("sphere","cube","cuboid","cylinder"):
            self.shape_type = "dense"
        self.shape = Shape3DFactory.create_shape("agent",config_elem.get("shape","point"), {key:val for key,val in config_elem.items()})
        self.shape.add_attachment(Shape3DFactory.create_shape("mark","circle", {"_id":"idle", "color":"red", "diameter":0.01}))
        self.position = Vector3D()
        self.orientation = Vector3D()
        self.start_position = Vector3D()
        self.start_orientation = Vector3D()
        temp_position = config_elem.get("position", None)
        if temp_position != None:
            self.position_from_dict = True
            try:
                self.start_position = Vector3D(temp_position[_id][0],temp_position[_id][1],temp_position[_id][2])
            except:
                self.start_position = Vector3D(temp_position[-1][0],temp_position[-1][1],temp_position[-1][2])
            self.set_start_position(self.start_position)
        temp_orientation = config_elem.get("orientation", None)
        if temp_orientation != None:
            self.orientation_from_dict = True
            try:
                self.start_orientation = Vector3D(temp_orientation[_id][0],temp_orientation[_id][1],temp_orientation[_id][2])
            except:
                self.start_orientation = Vector3D(temp_orientation[-1][0],temp_orientation[-1][1],temp_orientation[-1][2])
            self.orientation = self.start_orientation
            self.set_start_orientation(self.start_orientation)
        self.shape.translate_attachments(self.start_orientation.x)

    def to_origin(self):
        self.position = Vector3D()
        self.shape.center = self.position
        self.shape.set_vertices()

    def set_start_position(self,new_position:Vector3D,_translate:bool = True):
        self.start_position = new_position
        self.set_position(new_position,_translate)

    def set_position(self,new_position:Vector3D,_translate:bool = True):
        self.position = new_position
        if _translate:
            self.shape.translate(self.position)

    def set_start_orientation(self,new_orientation:Vector3D):
        self.start_orientation = new_orientation
        self.set_orientation(new_orientation)

    def set_orientation(self,new_orientation:Vector3D):
        self.orientation = new_orientation
        self.shape.rotate(self.start_orientation.z)

    def get_start_position(self):
        return self.start_position
    
    def get_start_orientation(self):
        return self.start_orientation
    
    def get_position(self):
        return self.position

    def get_orientation(self):
        return self.orientation

    def close(self):
        del self.shape

    def get_shape(self):
        return self.shape

    def get_shape_type(self):
        return self.shape_type
    
class MovableObject(StaticObject):
    def __init__(self,entity_type:str, config_elem:dict,_id:int=0):
        super().__init__(entity_type,config_elem,_id)
        self.velocity = Vector3D()
        # self.max_absolute_velocity = 0.01
        # self.max_angular_velocity = 0.01

class MovableAgent(StaticAgent):

    STOP    = 0
    FORWARD = 1
    LEFT    = 2
    RIGHT   = 3

    def __init__(self,entity_type:str, config_elem:dict,_id:int=0):
        super().__init__(entity_type,config_elem,_id)
        self.velocity = Vector3D()
        self.moving_behavior = config_elem.get("moving_behavior","random_walk")
        self.max_absolute_velocity = 0.01 / self.ticks_per_second
        self.max_angular_velocity = 45 / self.ticks_per_second
        self.max_turning_ticks = 160
        self.standard_motion_steps = 5*16
        self.turning_ticks = 0
        self.forward_ticks = 0
        self.motion = MovableAgent.STOP
        self.last_motion_tick = 0
        self.crw_exponent = config_elem.get("crw_exponent",1) # 2 is brownian like motion
        self.levy_exponent = config_elem.get("levy_exponent",0.75) # 0 go straight often
        self.goal_position = None
        self.prev_orientation = Vector3D()
        self.position = Vector3D()
        self.prev_position = Vector3D()
        self.prev_goal_distance = 0
        self.forward_vector = Vector3D()
    
    def get_max_absolute_velocity(self):
        return self.max_absolute_velocity
    
    def get_prev_position(self):
        return self.prev_position
    
    def get_prev_orientation(self):
        return self.prev_orientation
    
    def get_forward_vector(self):
        return self.forward_vector

    def set_start_orientation(self,new_orientation:Vector3D):
        super().set_start_orientation(new_orientation)
        
    def set_orientation(self,new_orientation:Vector3D):
        super().set_orientation(new_orientation)

    def random_walk(self,tick):
        if self.motion == MovableAgent.LEFT or self.motion == MovableAgent.RIGHT or self.motion == MovableAgent.STOP:
            if tick > self.last_motion_tick + self.turning_ticks:
                self.last_motion_tick = tick
                self.motion = MovableAgent.FORWARD
                self.forward_ticks = abs(levy(self.random_generator,self.standard_motion_steps,self.levy_exponent))
        elif self.motion == MovableAgent.FORWARD:
            if tick > self.last_motion_tick + self.forward_ticks:
                self.last_motion_tick = tick
                p = Random.uniform(self.random_generator,0,1)
                if p < 0.5: self.motion = MovableAgent.LEFT
                else: self.motion = MovableAgent.RIGHT
                angle = Random.uniform(self.random_generator,0,math.pi) if self.crw_exponent == 0 else abs(wrapped_cauchy_pp(self.random_generator,self.crw_exponent))
                self.turning_ticks = int(angle * self.max_turning_ticks)

    def random_way_point(self,arena_shape):
        if self.goal_position == None or math.sqrt((self.position.x - self.goal_position.x)**2 + (self.position.y - self.goal_position.y)**2) <= .001:
            self.goal_position = self.shape._get_random_point_inside_shape(self.random_generator, arena_shape)
        angle_to_goal = normalize_angle((math.atan2(self.position.y - self.goal_position.y, self.position.x - self.goal_position.x)/math.pi)*180 + self.orientation.z)
        distance = self.position - self.goal_position
        if abs(distance.magnitude()) >= self.prev_goal_distance:
            self.last_motion_tick += 1
        self.prev_goal_distance = distance.magnitude()
        if self.last_motion_tick > self.ticks_per_second*.5:
            self.last_motion_tick = 0
            self.goal_position = None
        if angle_to_goal >= self.max_angular_velocity:
            self.motion = MovableAgent.LEFT
        elif angle_to_goal <= -self.max_angular_velocity:
            self.motion = MovableAgent.RIGHT
        else:
            self.motion = MovableAgent.FORWARD

    def post_step(self,position_correction):
        if position_correction != None:
            self.position = position_correction
            self.shape.translate(self.position)
            self.shape.translate_attachments(self.orientation.z)
    
    def run(self,tick,arena_shape):
        if self.moving_behavior == "random_walk":
            self.random_walk(tick)
        elif self.moving_behavior == "random_way_point":
            self.random_way_point(arena_shape)
        self.prev_position = self.position
        self.prev_orientation = self.orientation
        delta_orientation = Vector3D(0,0,0)
        if self.motion == MovableAgent.LEFT:
            delta_orientation = Vector3D(0,0,self.max_angular_velocity)
        elif self.motion == MovableAgent.RIGHT:
            delta_orientation = Vector3D(0,0,-self.max_angular_velocity)
        self.orientation = self.orientation + delta_orientation
        self.orientation.z = self.orientation.z%360
        angle_rad = math.radians(self.orientation.z)
        self.forward_vector = Vector3D(self.max_absolute_velocity * math.cos(angle_rad),
                                        self.max_absolute_velocity * -math.sin(angle_rad),
                                        0)
        self.position = self.position + self.forward_vector
        self.shape.rotate(delta_orientation.z)
        self.shape.translate(self.position)
        self.shape.translate_attachments(self.orientation.z)

def wrapped_cauchy_pp(random_generator,c:float) -> float:
    q = 0.5
    u = Random.uniform(random_generator,0,1)
    val = (1 - c) / (1 + c)
    return 2 * math.atan(val * math.tanh(math.pi * (u - q)))

def levy(random_generator,c:float,alpha:float) -> int:
    u = math.pi * (Random.uniform(random_generator,0,1) - 0.5)
    if alpha == 1:
        t = math.tan(u)
        return (int)(c * t)
    v = 0
    while v == 0: v = exponential_distribution(random_generator,1)
    if alpha == 2:
        t = 2 * math.sin(u) * math.sqrt(v)
        return (int)(c * t)
    t = math.sin(alpha * u) / math.pow(math.cos(u), 1 / alpha)
    s = math.pow(math.cos((1 - alpha) * u) / v,(1- alpha) / alpha)
    return (int)(c * t * s)
    
def exponential_distribution(random_generator,alpha):
    u = Random.uniform(random_generator,0,1)
    x = (-alpha) * math.log(1 - u)
    return x

def normalize_angle(angle:float):
    while angle > 180:
        angle -= 360
    while angle < -180:
        angle += 360
    return angle