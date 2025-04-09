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
        self.shape_type = None
        self.shape = None
        self.position_from_dict = False
        self.color = config_elem.get("color","gray")
    
    def get_name(self):
        return self.entity_type+"_"+str(self._id)

    def get_shape_type(self):
        return self.shape_type

    def get_position_from_dict(self):
        return self.position_from_dict
    
    def get_orientation_from_dict(self):
        return self.orientation_from_dict

    def get_shape(self):
        return self.shape

    def reset(self):
        pass

    def close(self):
        del self.shape

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
        if config_elem.get("shape") in ("circle","square","rectangle"):
            self.entity_type += "_"+str(config_elem.get("shape"))
            self.shape_type = "flat"
            self.shape = Shape3DFactory.create_shape("object",config_elem.get("shape"), {key:val for key,val in config_elem.items()}) if self.shape_type != None else None
        elif config_elem.get("shape") in ("sphere","cube","cuboid","cylinder"):
            self.entity_type += "_"+str(config_elem.get("shape"))
            self.shape_type = "dense"
            self.shape = Shape3DFactory.create_shape("object",config_elem.get("shape"), {key:val for key,val in config_elem.items()}) if self.shape_type != None else None
        else: raise ValueError(f"Invalid object type: {self.entity_type}")
        logging.info(f"Object {self.entity_type} id {self._id} intialized")

class Agent(Entity):
    def __init__(self,entity_type:str, config_elem: dict,_id:int=0):
        super().__init__(entity_type,config_elem,_id)
        self.ticks_per_second = config_elem.get("ticks_per_second",31)
        self.random_generator = None
        self.color = config_elem.get("color","blue")
        if config_elem.get("shape") in ("sphere","cube","cuboid","cylinder"):
            self.shape_type = "dense"
            self.shape = Shape3DFactory.create_shape("agent",config_elem.get("shape"), {key:val for key,val in config_elem.items()}) if self.shape_type != None else None
        logging.info(f"Agent {self.entity_type} id {self._id} intialized")
    
    def ticks(self): return self.ticks_per_second
    
    def set_random_generator(self,randomn_generator):
        self.random_generator = randomn_generator

    def run(self):
        pass
    
class StaticObject(Object):
    def __init__(self,entity_type:str, config_elem:dict,_id:int=0):
        super().__init__(entity_type,config_elem,_id)
        self.position = Vector3D()
        self.orientation = Vector3D()
        self.start_position = None
        self.start_orientation = None
        self.position_from_dict = False
        self.orientation_from_dict = False
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
        self.shape.rotate_x(self.start_orientation.x)
        self.shape.rotate_y(self.start_orientation.y)
        self.shape.rotate_z(self.start_orientation.z)

    def get_start_position(self):
        return self.start_position
    
    def get_start_orientation(self):
        return self.start_orientation
    
    def get_position(self):
        return self.position

    def get_orientation(self):
        return self.orientation
    
class StaticAgent(Agent):
    def __init__(self,entity_type:str, config_elem:dict,_id:int=0):
        super().__init__(entity_type,config_elem,_id)
        self.position = Vector3D()
        self.orientation = Vector3D()
        self.start_position = None
        self.start_orientation = None
        self.position_from_dict = False
        self.orientation_from_dict = False
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
        self.shape.rotate_x(self.start_orientation.x)
        self.shape.rotate_y(self.start_orientation.y)
        self.shape.rotate_z(self.start_orientation.z)

    def get_start_position(self):
        return self.start_position
    
    def get_start_orientation(self):
        return self.start_orientation
    
    def get_position(self):
        return self.position

    def get_orientation(self):
        return self.orientation

class MovableObject(StaticObject):
    def __init__(self,entity_type:str, config_elem:dict,_id:int=0):
        super().__init__(entity_type,config_elem,_id)
        self.velocity = Vector3D()
        # self.max_absolute_velocity = 0.01
        # self.max_angular_velocity = 0.01

class MovableAgent(StaticAgent):
    def __init__(self,entity_type:str, config_elem:dict,_id:int=0):
        super().__init__(entity_type,config_elem,_id)
        self.velocity = Vector3D()
        self.max_absolute_velocity = 0.01 / self.ticks_per_second
        self.max_angular_velocity = 0.01 / self.ticks_per_second

    def run(self,arena_shape):
        self.prev_orientation = self.orientation
        self.prev_position = self.position
        delta_orientation = Vector3D(0,0,
                                     Random.uniform(self.random_generator,0,self.max_angular_velocity))
        self.orientation = self.orientation + delta_orientation
        self.shape.rotate_z(delta_orientation.z)
        forward_vector = Vector3D(self.max_absolute_velocity * -math.sin(math.radians(self.orientation.z)),
                                  self.max_absolute_velocity * math.cos(math.radians(self.orientation.z)),
                                  0)
        self.position = self.position + forward_vector
        self.shape.translate(self.position)
        if self.shape.check_overlap(arena_shape):
            # Calculate the normal vector of the arena border at the collision point
            collision_normal = self.shape.get_collision_normal(arena_shape)
            
            # Project the velocity vector onto the tangent of the collision surface
            velocity_projection = self.velocity - collision_normal * (self.velocity.dot(collision_normal))
            
            # Adjust orientation to align with the sliding direction
            slide_angle = math.degrees(math.atan2(velocity_projection.y, velocity_projection.x))
            self.orientation.z = slide_angle
            self.shape.rotate_z(self.orientation.z - self.prev_orientation.z)
            
            # Update position and orientation based on the projected velocity
            self.position = self.prev_position + velocity_projection
            self.shape.translate(self.position - self.prev_position)