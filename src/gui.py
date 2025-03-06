import logging

class GuiFactory():
    factories = {}

    @staticmethod
    def create_gui(config_elem:dict):
        if config_elem.get("_id") in ("2D","abstract"):
            return GUI_2D(config_elem)
        elif config_elem.get("_id") == "3D":
            return GUI_3D(config_elem)
        else:
            raise ValueError(f"Invalid gui type: {config_elem.gui['_id']} valid types are '2D' or '3D'")

class GUI():

    def __init__(self,config_elem:dict):
        pass

class GUI_2D(GUI):

    def __init__(self,config_elem:dict):
        self._id = "2D"
        if config_elem.get("_id") == "abstract":
            pass
        else:
            pass
        logging.info("2D GUI created successfully")
        
class GUI_3D(GUI):

    def __init__(self,config_elem:dict):
        if config_elem.get("_id") == "abstract":
            logging.info("Switching to 2D GUI")
            GUI_2D(config_elem)
        else:
            self._id = "3D"
            logging.info("3D GUI created successfully")