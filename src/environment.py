import logging
from config import Config
from arena import ArenaFactory
from gui import GuiFactory

class EnvironmentFactory():

    @staticmethod
    def create_environment(config_elem:Config):
        if not config_elem.environment["multi_processing"] or config_elem.gui["render"]:
            return SingleProcessEnvironment(config_elem)
        elif config_elem.environment["multi_processing"] and not config_elem.gui["render"]:
            return MultiProcessEnvironment(config_elem)
        else:
            raise ValueError(f"Invalid environment configuration: {config_elem.environment['multi_processing']} {config_elem.gui['render']}")
        
class Environment():
    
    def __init__(self,config_elem:Config):
        self.experiments = config_elem.parse_experiments()


class SingleProcessEnvironment(Environment):
    
    def __init__(self,config_elem:Config):
        super().__init__(config_elem)
        logging.info("Single process environment created successfully")
        for exp in self.experiments:
            my_gui = None
            if exp.gui["render"]:
                my_gui = GuiFactory.create_gui(exp)
            my_arena = ArenaFactory.create_arena(exp,my_gui)
            my_arena.initialize()
            my_arena.run()
            my_arena.close()
        logging.info("All experiments completed successfully")
            

class MultiProcessEnvironment(Environment):
    
    def __init__(self,config_elem:Config):
        super().__init__(config_elem)
        logging.info("Multi process environment created successfully")
