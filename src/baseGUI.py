class BaseGuiFactory():
    factories = {}

    @staticmethod
    def create_base_gui(config_elem:object):
        return BaseGuiFactory.factories[config_elem._id].create(config_elem)
    
    @staticmethod
    def add_factory(_id, factory):
        BaseGuiFactory.factories[_id] = factory

class baseGUI():

    class Factory:
        def create(self, config_elem:object): return baseGUI(config_elem)

    def __init__(self):
        pass