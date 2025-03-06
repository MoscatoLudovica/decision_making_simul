import logging, gc
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
        self.num_runs = int(config_elem.environment.get("num_runs"))
        self.time_limit = int(config_elem.environment.get("time_limit"))
        self.gui_id = config_elem.gui.get("_id","2D")
        self.render = [config_elem.environment.get("render",False),config_elem.gui,True and config_elem.environment.get("render",False)]
        self.gui = None
        self.arena = None

    def start(self):
        pass

class SingleProcessEnvironment(Environment):
    
    def __init__(self,config_elem:Config):
        super().__init__(config_elem)
        logging.info("Single process environment created successfully")
    
    def start(self):
        self.arena_shape="none"
        for exp in self.experiments:
            self.arena = ArenaFactory.create_arena(exp)
            new_arena_shape = self.arena.get_id()
            if self.render[0] and self.arena_shape != new_arena_shape:
                self.arena_shape = new_arena_shape
                self.render[2] = True
            if self.render[2] and self.render[0]:
                self.render[1]["_id"] = "abstract" if self.arena_shape in (None,"none") else self.gui_id
                self.gui = GuiFactory.create_gui(self.render[1])
                self.render[2] = False
            if self.num_runs > 1 and self.arena.get_seed() < 0: self.arena.reset_seed()
            self.arena.initialize()
            for run in range(1,self.num_runs + 1):
                logging.info(f"Run number {run} started")
                for _ in range(self.time_limit):
                    self.arena.run()
                self.arena.increment_seed()
                if run < self.num_runs: self.arena.reset()
            gc.collect()
        logging.info("All experiments completed successfully")
    
class MultiProcessEnvironment(Environment):
    
    def __init__(self,config_elem:Config):
        super().__init__(config_elem)
        logging.info("Multi process environment created successfully")

    def start(self):
        pass