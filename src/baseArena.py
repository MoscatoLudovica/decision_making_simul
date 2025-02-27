class BaseArenaFactory():
    factories = {}

    @staticmethod
    def create_base_arena(config_elem:object):
        return BaseArenaFactory.factories[config_elem._id].create(config_elem)
    
    @staticmethod
    def add_factory(_id, factory):
        BaseArenaFactory.factories[_id] = factory

class BaseArena():
    
    class Factory:
        def create(self, config_elem:object): return BaseArena(config_elem)
    
    def __init__(self,config_elem:object):
        return