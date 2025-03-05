class DataHandlingFactory():
    
    @staticmethod
    def create_data_handling(config_elem:object):
        return DataHandling(config_elem)

class DataHandling():
     
    def __init__(self,config_elem:object):
        pass
    