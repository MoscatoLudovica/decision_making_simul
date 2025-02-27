class BaseLogicEntityFactory:
    factories = {}
    
    @staticmethod
    def create_base_logic_entity(config_elem: object):
        return BaseLogicEntityFactory.factories[config_elem._id].create(config_elem)
    
    @staticmethod
    def add_factory(_id, factory):
        BaseLogicEntityFactory.factories[_id] = factory

class BaseLogicEntity:
    
    class Factory:
        def create(self, config_elem: object): return BaseLogicEntity(config_elem)
    
    def __init__(self, config_elem: object):
        self.config_elem = config_elem

    def perform_logic(self):
        # Placeholder method for logic operations
        pass
