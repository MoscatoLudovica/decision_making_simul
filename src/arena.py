import logging
from random import Random
from src.bodies.shapes2D import Shape2DFactory
from src.bodies.shapes3D import Shape3DFactory
from entity import EntityFactory
from gui import GUI_2D, GUI_3D

class ArenaFactory():

    @staticmethod
    def create_arena(config_elem:object):
        if config_elem.arena["_id"] == "abstract" or config_elem.arena["_id"] == "none":
            return AbstractArena(config_elem)
        elif config_elem.arena["_id"] == "circle":
            return CircularArena(config_elem)
        elif config_elem.arena["_id"] == "rectangle":
            return RectangularArena(config_elem)
        elif config_elem.arena["_id"] == "square":
            return SquareArena(config_elem)
        else:
            raise ValueError(f"Invalid arena type: {config_elem.arena['_id']}")

class Arena():
    
    def __init__(self, config_elem:object, gui:object):
        self._id = config_elem.arena["_id"]
        self.agents = {agent_type: [] for agent_type in config_elem.arena.get("agents", {}).keys()}
        shape_type = config_elem.arena.get("_id", "none")
        if shape_type == "abstract": shape_type = "none"
        self.shape = Shape2DFactory.create_shape(shape_type, config_elem.arena)
        self.objects = {object_type: [] for object_type in config_elem.arena.get("objects", {}).keys()}
        self.gui = gui
        self.ticks_per_second = config_elem.arena.get("ticks_per_second", 10)
        self.time_limit = config_elem.environment.get("time_limit", 1000)
        self.ticks_limit = self.time_limit * self.ticks_per_second
        self.random_seed = config_elem.environment.get("random_seed", -1)
        self.num_runs = config_elem.environment.get("num_runs", 1)
        self.random_generator = Random()
        self.current_run = 0

    def set_random_seed(self):
        if self.num_runs > 1:
            self.random_generator.seed(self.current_run)
        else:
            if self.random_seed > -1:
                self.random_generator.seed(self.random_seed)
            else:
                self.random_generator.seed()

    def initialize(self):
        self.elapsed_ticks = 0
        self.current_run += 1
        self.set_random_seed()
        if self.gui is not None:
            self.gui.initialize()
    
    def run(self):
        for _ in range(self.num_runs):
            logging.info(f"Starting run {self.current_run}/{self.num_runs}")
            try:
                while self.elapsed_ticks < self.ticks_limit:
                    for _ in range(self.ticks_per_second):
                        self.update()
            except KeyboardInterrupt:
                logging.info("Simulation interrupted by user")
                break
            logging.info(f"Run {self.current_run}/{self.num_runs} completed")
            if self.current_run < self.num_runs: self.initialize()
        logging.info("All runs completed")

    def update(self):
        for agent_type, agents in self.agents.items():
            for agent in agents:
                agent.update(self.ticks_per_second,self.shape,self.objects)
        for object_type, objects in self.objects.items():
            for obj in objects:
                obj.update()
        if self.gui is not None:
            self.gui.update()
        self.elapsed_ticks += 1

    def close(self):
        if self.gui is not None:
            self.gui.close()


class AbstractArena(Arena):
    
    def __init__(self, config_elem:object, gui:object):
        super().__init__(config_elem, gui)
        logging.info("Abstract arena created successfully")

    def initialize(self):
        super().initialize()
    
    def run(self):
        super().run()
    
    def update(self):
        super().update()
    
    def close(self):
        super().close()

class CircularArena(Arena):
    
    def __init__(self, config_elem:object, gui:object):
        super().__init__(config_elem, gui)
        self.height = config_elem.arena.get("height", 1)
        self.radius = config_elem.arena.get("radius", 1)
        self.color = config_elem.arena.get("color", "white")
        logging.info("Circular arena created successfully")

    def initialize(self):
        super().initialize()
    
    def run(self):
        super().run()
    
    def update(self):
        super().update()
    
    def close(self):
        super().close()

class RectangularArena(Arena):
    
    def __init__(self, config_elem:object, gui:object):
        super().__init__(config_elem, gui)
        self.height = config_elem.arena.get("height", 1)
        self.length = config_elem.arena.get("length", 1)
        self.width = config_elem.arena.get("width", 1)
        self.color = config_elem.arena.get("color", "white")
        logging.info("Rectangular arena created successfully")

    def initialize(self):
        super().initialize()
    
    def run(self):
        super().run()
    
    def update(self):
        super().update()
    
    def close(self):
        super().close()

class SquareArena(Arena):
    
    def __init__(self, config_elem:object, gui:object):
        super().__init__(config_elem, gui)
        self.height = config_elem.arena.get("height", 1)
        self.side = config_elem.arena.get("side", 1)
        self.color = config_elem.arena.get("color", "white")
        logging.info("Square arena created successfully")

    def initialize(self):
        super().initialize()
    
    def run(self):
        super().run()
    
    def update(self):
        super().update()
    
    def close(self):
        super().close()