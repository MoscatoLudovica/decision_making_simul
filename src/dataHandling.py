import os
from config import Config
class DataHandlingFactory():
    
    @staticmethod
    def create_data_handling(config_elem:Config):
        if config_elem.arena.get("_id") in ("abstract", "none", None):
            return DataHandling(config_elem)
        else:
            return SpaceDataHandling(config_elem)

class DataHandling():

    def __init__(self,config_elem:Config):
        data_path = os.path.join(os.path.abspath(""),config_elem.results.get("base_path","../"))
        if not os.path.exists(data_path): os.mkdir(data_path)
class SpaceDataHandling(DataHandling):
     
    def __init__(self,config_elem:Config):
        super().__init__(config_elem)
    