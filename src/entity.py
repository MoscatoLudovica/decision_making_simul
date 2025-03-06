import logging, threading
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
class ThdEntity(threading.Thread):    
    def __init__(self,entity_type:str, config_elem: object,_id:int=0):
        super().__init__()
        self.entity_type = entity_type
        self._id = _id
        logging.info(f"Agent {self.entity_type} id {self._id} intialized")

class StaticObjectEntity(Entity):
    def __init__(self,entity_type:str, config_elem:dict,_id:int=0):
        super().__init__(entity_type,config_elem,_id)

class MovableObjectEntity(Entity):
    def __init__(self,entity_type:str, config_elem:dict,_id:int=0):
        super().__init__(entity_type,config_elem,_id)


class StaticAgentEntity(ThdEntity):
    def __init__(self,entity_type:str, config_elem:dict,_id:int=0):
        super().__init__(entity_type,config_elem,_id)

class MovableAgentEntity(ThdEntity):
    def __init__(self,entity_type:str, config_elem:dict,_id:int=0):
        super().__init__(entity_type,config_elem,_id)

    