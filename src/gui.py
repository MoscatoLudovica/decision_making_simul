import logging
from config import Config

class GuiFactory():
    factories = {}

    @staticmethod
    def create_gui(config_elem:object):
        if config_elem.gui["_id"] == "2D":
            return GUI_2D(config_elem)
        elif config_elem.gui["_id"] == "3D":
            return GUI_3D(config_elem)
        else:
            raise ValueError(f"Invalid gui type: {config_elem.gui['_id']}")

class GUI():

    def __init__(self,config_elem:Config):
        pass

class GUI_2D(GUI):

    def __init__(self,config_elem:Config):
        super().__init__()
        if config_elem.arena["shape"] == "abstract":
            logging.info("Initializing network representation")
        else:
            logging.info("Initializing arena representation")
        logging.info("2D GUI created successfully")
        
class GUI_3D(GUI):

    def __init__(self,config_elem:Config):
        super().__init__()
        if config_elem.arena["shape"] == "abstract":
            logging.info("Switching to 2D GUI")
            GUI_2D(config_elem)
        else:
            logging.info("Initializing arena representation")
            logging.info("3D GUI created successfully")