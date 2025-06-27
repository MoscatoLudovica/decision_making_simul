import os,json,csv
from config import Config

class DataHandlingFactory():
    @staticmethod
    def create_data_handling(config_elem: Config):
        if config_elem.arena.get("_id") in ("abstract", "none", None):
            return DataHandling(config_elem)
        else:
            return SpaceDataHandling(config_elem)

class DataHandling():
    def __init__(self, config_elem: Config):
        base_path = config_elem.results.get("base_path", "../data/")
        abs_base_path = os.path.join(os.path.abspath(""), base_path)
        os.makedirs(abs_base_path, exist_ok=True)
        existing = [d for d in os.listdir(abs_base_path) if d.startswith("config_folder_")]
        folder_id = len(existing)
        self.config_folder = os.path.join(abs_base_path, f"config_folder_{folder_id}")
        if os.path.exists(self.config_folder):
            raise Exception(f"Error config folder {self.config_folder} already present")
        os.mkdir(self.config_folder)
        with open(os.path.join(self.config_folder, "config.json"), "w") as f:
            json.dump(config_elem.__dict__, f, indent=4, default=str)
        self.agents_files = {}

    def new_run(self, run: int, shapes, spins):
        self.run_folder = os.path.join(self.config_folder, f"run_{run}")
        if os.path.exists(self.run_folder):
            raise Exception(f"Error run folder {self.run_folder} already present")
        os.mkdir(self.run_folder)

    def save(self, shapes, spins):
        pass

    def close(self, shapes):
        pass

class SpaceDataHandling(DataHandling):
    def __init__(self, config_elem: Config):
        super().__init__(config_elem)

    def new_run(self, run: int, shapes, spins):
        super().new_run(run, shapes, spins)
        if shapes is not None:
            for key, entities in shapes.items():
                for idx, entity in enumerate(entities):
                    file_path = os.path.join(self.run_folder, f"position_{key}_{idx}.csv")
                    if os.path.exists(file_path):
                        raise Exception(f"Error: file {file_path} already exists")
                    f = open(file_path, "w+", newline="")
                    writer = csv.writer(f)
                    com = entity.center_of_mass()
                    writer.writerow(["x", "y", "z"])
                    writer.writerow([f"{com.x:.5f}", f"{com.y:.5f}", f"{com.z:.5f}"])
                    self.agents_files[f"position_{key}_{idx}"] = (f, writer)

    def save(self, shapes, spins):
        if shapes is not None:
            for key, entities in shapes.items():
                for idx, entity in enumerate(entities):
                    com = entity.center_of_mass()
                    file_writer = self.agents_files[f"position_{key}_{idx}"][1]
                    file_writer.writerow([f"{com.x:.5f}", f"{com.y:.5f}", f"{com.z:.5f}"])

    def close(self, shapes):
        if shapes is not None:
            for key, entities in shapes.items():
                for idx, _ in enumerate(entities):
                    file_handle = self.agents_files[f"position_{key}_{idx}"][0]
                    file_handle.flush()
                    file_handle.close()
            self.agents_files.clear()