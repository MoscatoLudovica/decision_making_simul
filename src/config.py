import json

class Config:
    def __init__(self, config_path):
        self.config_path = config_path
        self.data = self.load_config()

    def load_config(self):
        with open(self.config_path, 'r') as file:
            return json.load(file)

    @property
    def mode(self):
        return self.data.get('mode', {})

    @property
    def environment(self):
        return self.data.get('environment', {})

    @property
    def objects(self):
        return self.data.get('objects', {})

    @property
    def agents(self):
        return self.data.get('agents', {})

    @property
    def results(self):
        return self.data.get('results', {})

    @property
    def gui(self):
        return self.data.get('gui', {})
