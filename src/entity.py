class EntityFactory:
    
    @staticmethod
    def create_entity(config_elem: object):
        return Entity(config_elem)
    
class Entity:
    
    def __init__(self, config_elem: object):
        self.config_elem = config_elem

    def perform_logic(self):
        # Placeholder method for logic operations
        pass
