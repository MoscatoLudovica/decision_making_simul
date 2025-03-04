import logging
from gui import GUI_2D, GUI_3D

class ArenaFactory():
    factories = {}

    @staticmethod
    def create_arena(config_elem:object):
        if config_elem.arena["_id"] == "abstract":
            return AbstractArena(config_elem)
        if config_elem.arena["_id"] == "circle":
            return CircularArena(config_elem)
        elif config_elem.arena["_id"] == "rectangle":
            return RectangularArena(config_elem)
        elif config_elem.arena["_id"] == "square":
            return SquareArena(config_elem)
        else:
            logging.fatal(f"Invalid arena type: {config_elem.arena['_id']}")
            return None

class Arena():
    
    def __init__(self,config_elem:object,gui:object):
        self.shape = config_elem.arena["_id"]
        self.height = config_elem.arena.get("height", 1)
        self.gui = gui

class AbstractArena(Arena):
    
    def __init__(self,config_elem:object,gui:object):
        super().__init__(config_elem)
        logging.info("Abstract arena created successfully")

class CircularArena(Arena):
    
    def __init__(self,config_elem:object,gui:object):
        super().__init__(config_elem)
        self.radius = config_elem.arena["radius"]
        self.color = config_elem.arena["color"]
        logging.info("Circular arena created successfully")

class RectangularArena(Arena):
    
    def __init__(self,config_elem:object,gui:object):
        super().__init__(config_elem)
        self.length = config_elem.arena["length"]
        self.width = config_elem.arena["width"]
        self.color = config_elem.arena["color"]
        logging.info("Rectangular arena created successfully")

class SquareArena(Arena):
    
    def __init__(self,config_elem:object,gui:object):
        super().__init__(config_elem)
        self.side = config_elem.arena["side"]
        self.color = config_elem.arena["color"]
        logging.info("Square arena created successfully")