import os,json,csv
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
        self.config_folder = os.path.join(os.path.abspath(""),config_elem.results.get("base_path","../"))
        if not os.path.exists(self.config_folder): os.mkdir(self.config_folder)
        folder_id = 0
        for _ in os.listdir(self.config_folder):
            folder_id += 1
        self.config_folder = os.path.join(self.config_folder,f"config_folder_{folder_id}")
        if os.path.exists(self.config_folder): raise Exception(f"Error config folder {self.config_folder} already present")
        os.mkdir(self.config_folder)
        # Save config_elem as JSON in self.config_folder
        with open(os.path.join(self.config_folder, "config.json"), "w") as f:
            json.dump(config_elem.__dict__, f, indent=4, default=str)
        self.agents_files = {}

    def new_run(self,run:int,shapes,spins):
        self.run_folder = os.path.join(self.config_folder, f"run_{run}")
        if os.path.exists(self.run_folder):
            raise Exception(f"Error run folder {self.run_folder} already present")
        os.mkdir(self.run_folder)

    def save(self,shapes,spins):
        pass
    
    def close(self,shapes):
        pass

class SpaceDataHandling(DataHandling):
    def __init__(self,config_elem:Config):
        super().__init__(config_elem)

    def new_run(self,run:int,shapes,spins):
        super().new_run(run,shapes,spins)
        if shapes is not None:
            for key, entities in shapes.items():
                for idx, entity in enumerate(entities):
                    file_path = os.path.join(self.run_folder, f"position_{key}_{idx}.csv")
                    if os.path.exists(file_path): raise Exception(f"Error: file {file_path} already exists")
                    f = open(file_path, "w+",newline="")
                    writer = csv.writer(f)
                    com = entity.center_of_mass()
                    writer.writerow(["x", "y", "z"])
                    writer.writerow([format(com.x, '.5f'), format(com.y, '.5f'), format(com.z, '.5f')])
                    self.agents_files[f"position_{key}_{idx}"] = (f, writer)

    def save(self,shapes,spins):
        if shapes is not None:
            for key, entities in shapes.items():
                for idx, entity in enumerate(entities):
                    com = entity.center_of_mass()
                    self.agents_files[f"position_{key}_{idx}"][1].writerow([format(com.x, '.5f'), format(com.y, '.5f'), format(com.z, '.5f')]) 
    
    def close(self,shapes):
        if shapes is not None:
            for key, entities in shapes.items():
                for idx, entity in enumerate(entities):
                    self.agents_files[f"position_{key}_{idx}"][0].flush()               
                    self.agents_files[f"position_{key}_{idx}"][0].close()
            self.agents_files.clear()     