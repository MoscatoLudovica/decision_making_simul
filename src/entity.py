import logging, threading
from geometry_utils.vector3D import Vector3D
class EntityFactory:
    
    @staticmethod
    def create_entity(entity_type:str,config_elem: object,_id:int=0):
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
    def __init__(self,entity_type:str, config_elem: object,_id:int=0):
        self.entity_type = entity_type
        self._id = _id
        if config_elem.get("_id") in ("idle","interactive"):
            self.entity_type += "_"+str(config_elem.get("_id"))
        else: raise ValueError(f"Invalid object type: {self.entity_type}")
        if config_elem.get("shape") in ("circle","square","rectangle","triangle","polygon"):
            self.entity_type += "_"+str(config_elem.get("shape"))
            self.shape = "flat"
        elif config_elem.get("shape") in ("sphere","cube","cuboid","pyramid","cone","cylinder","polygon"):
            self.entity_type += "_"+str(config_elem.get("shape"))
            self.shape = "dense"
        else: raise ValueError(f"Invalid object type: {self.entity_type}")
        logging.info(f"Object {self.entity_type} id {self._id} intialized")
    
    def get_name(self):
        return self.entity_type+"_"+str(self._id)

    def get_shape(self):
        return self.shape

    def reset(self):
        pass

    def entity(self) -> str:
        return self.entity_type

class ThdEntity(threading.Thread):    
    def __init__(self,entity_type:str, config_elem: object,_id:int=0):
        super().__init__()
        self.entity_type = entity_type
        self._id = _id
        logging.info(f"Agent {self.entity_type} id {self._id} intialized")

    def get_name(self):
        return self.entity_type+"_"+str(self._id)

    def reset(self):
        pass

    def entity(self) -> str:
        return self.entity_type
    
class StaticObjectEntity(Entity):
    def __init__(self,entity_type:str, config_elem:dict,_id:int=0):
        super().__init__(entity_type,config_elem,_id)
        self.position = Vector3D()
        self.start_position = Vector3D()

    def set_start_position(self,new_position:Vector3D):
        self.position = new_position
        self.start_position =self.position

    def set_position(self,new_position:Vector3D):
        self.position = new_position

    def set_angle(self,new_angle:float):
        self.angle = new_angle

    def get_position(self):
        return self.position

    def get_angle(self):
        return self.angle
    
class MovableObjectEntity(StaticObjectEntity):
    def __init__(self,entity_type:str, config_elem:dict,_id:int=0):
        super().__init__(entity_type,config_elem,_id)
        self.velocity = Vector3D()
        self.max_absolute_velocity = 0.0
        self.max_angular_velocity = 0.0

class StaticAgentEntity(ThdEntity):
    def __init__(self,entity_type:str, config_elem:dict,_id:int=0):
        super().__init__(entity_type,config_elem,_id)
        self.position = Vector3D()
        self.start_position = Vector3D()

    def set_start_position(self,new_position:Vector3D):
        self.position = new_position
        self.start_position =self.position

    def set_angle(self,new_angle:float):
        self.angle = new_angle

    def set_position(self,new_position:Vector3D):
        self.position = new_position

    def get_position(self):
        return self.position
    
    def get_angle(self):
        return self.angle
    
class MovableAgentEntity(StaticAgentEntity):
    def __init__(self,entity_type:str, config_elem:dict,_id:int=0):
        super().__init__(entity_type,config_elem,_id)
        self.velocity = Vector3D()
        self.max_absolute_velocity = 0.0
        self.max_angular_velocity = 0.0
    