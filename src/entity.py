import logging, threading
from geometry_utils.vector3D import Vector3D
from bodies.shapes3D import Shape3DFactory
class EntityFactory:
    
    @staticmethod
    def create_entity(entity_type:str,config_elem: dict,_id:int=0):
        check_type = entity_type.split('_')[0]+'_'+entity_type.split('_')[1]
        if check_type == "agent_static":
            return StaticAgentEntity(entity_type,config_elem,_id)
        elif check_type == "agent_movable":
            return MovableAgentEntity(entity_type,config_elem,_id)
        elif check_type == "object_static":
            return StaticObjectEntity(entity_type,config_elem,_id)
        elif check_type == "object_movable":
            return MovableObjectEntity(entity_type,config_elem,_id)
        else:
            raise ValueError(f"Invalid agent type: {entity_type}")
    
class Entity:    
    def __init__(self,entity_type:str, config_elem: dict,_id:int=0):
        self.entity_type = entity_type
        self._id = _id
        self.shape_type = None
        self.shape = None
        self.position_from_dict = False
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
    
    def get_name(self):
        return self.entity_type+"_"+str(self._id)

    def get_shape_type(self):
        return self.shape_type

    def get_position_from_dict(self):
        return self.position_from_dict

    def get_shape(self):
        return self.shape

    def reset(self):
        pass

    def close(self):
        del self.shape


    def entity(self) -> str:
        return self.entity_type

class ThdEntity(threading.Thread):    
    def __init__(self,entity_type:str, config_elem: dict,_id:int=0):
        super().__init__()
        self.entity_type = entity_type
        self._id = _id
        self.ticks_per_second = config_elem.get("ticks_per_second",1)
        self.shape_type = None
        self.shape = None
        self.position_from_dict = False
        self.color = config_elem.get("color","blue")
        if config_elem.get("shape") in ("sphere","cube","cuboid","cylinder"):
            self.shape_type = "dense"
            self.shape = Shape3DFactory.create_shape("agent",config_elem.get("shape"), {key:val for key,val in config_elem.items()}) if self.shape_type != None else None
        logging.info(f"Agent {self.entity_type} id {self._id} intialized")

    def get_name(self):
        return self.entity_type+"_"+str(self._id)

    def get_shape_type(self):
        return self.shape_type

    def get_position_from_dict(self):
        return self.position_from_dict
    
    def get_shape(self):
        return self.shape

    def reset(self):
        pass

    def close(self):
        del self.shape
        # kill thread
    def entity(self) -> str:
        return self.entity_type
    
class StaticObjectEntity(Entity):
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
            self.set_start_orientation(self.start_position)

    def set_start_position(self,new_position:Vector3D):
        self.position = new_position
        self.start_position = self.position
        self.shape.translate(self.start_position)

    def set_position(self,new_position:Vector3D,_translate:bool = True):
        self.position = new_position
        if _translate: self.shape.translate(self.position)

    def set_start_orientation(self,new_orientation:Vector3D):
        self.orientation = new_orientation
        self.start_orientation = self.orientation
        self.shape.rotate_x(self.start_orientation.x)
        self.shape.rotate_y(self.start_orientation.y)
        self.shape.rotate_z(self.start_orientation.z)

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

class StaticAgentEntity(ThdEntity):
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
                self.position = Vector3D(temp_position[_id][0],temp_position[_id][1],temp_position[_id][2])
            except:
                self.position = Vector3D(temp_position[-1][0],temp_position[-1][1],temp_position[-1][2])
            self.set_start_position(self.position)
        temp_orientation = config_elem.get("orientation", None)
        if temp_orientation != None:
            self.orientation_from_dict = True
            try:
                self.orientation = Vector3D(temp_orientation[_id][0],temp_orientation[_id][1],temp_orientation[_id][2])
            except:
                self.orientation = Vector3D(temp_orientation[-1][0],temp_orientation[-1][1],temp_orientation[-1][2])
            self.set_start_orientation(self.orientation)

    def set_start_position(self,new_position:Vector3D):
        self.position = new_position
        self.start_position =self.position
        self.shape.translate(self.start_position)

    def set_position(self,new_position:Vector3D,_translate:bool = True):
        self.position = new_position
        if _translate: self.shape.translate(self.position)

    def set_start_orientation(self,new_orientation:Vector3D):
        self.orientation = new_orientation
        self.start_orientation = self.orientation
        self.shape.rotate_x(self.start_orientation.x)
        self.shape.rotate_y(self.start_orientation.y)
        self.shape.rotate_z(self.start_orientation.z)

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
    
class MovableObjectEntity(StaticObjectEntity):
    def __init__(self,entity_type:str, config_elem:dict,_id:int=0):
        super().__init__(entity_type,config_elem,_id)
        self.velocity = Vector3D()
        self.max_absolute_velocity = 0.0
        self.max_angular_velocity = 0.0
    
class MovableAgentEntity(StaticAgentEntity):
    def __init__(self,entity_type:str, config_elem:dict,_id:int=0):
        super().__init__(entity_type,config_elem,_id)
        self.velocity = Vector3D()
        self.max_absolute_velocity = 0.0
        self.max_angular_velocity = 0.0
    