from baseLogicEntity import BaseLogicEntity, BaseLogicEntityFactory

class BasePhysicalEntityFactory():
    factories = {}
    
    @staticmethod
    def create_base_entity(config_elem: object):
        return BasePhysicalEntityFactory.factories[config_elem._id].create(config_elem)
    
    @staticmethod
    def add_factory(_id, factory):
        BasePhysicalEntityFactory.factories[_id] = factory
        
class BasePhysicalEntity():
     
    class Factory:
        def create(self, config_elem: object): return BasePhysicalEntity(config_elem)
    
    def __init__(self, config_elem: object):
        self.config_elem = config_elem
        self.logic_entity = None
    
    def attach_logic_entity(self, logic_entity: BaseLogicEntity):
        self.logic_entity = logic_entity