class BaseDataHandlingFactory():
    factories = {}
    @staticmethod
    def create_base_data_handling(config_elem:object):
        return BaseDataHandlingFactory.factories[config_elem._id].create(config_elem)
    @staticmethod
    def add_factory(_id, factory):
        BaseDataHandlingFactory.factories[_id] = factory

class BaseDataHandling():
     
    class Factory:
        def create(self, config_elem:object): return BaseDataHandling(config_elem)
    
    def __init__(self,config_elem:object):
        pass
    