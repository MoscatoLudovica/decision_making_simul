import logging, json

class Config:
    def __init__(self, config_path: str = None, new_data: dict = None):
        if config_path:
            self.config_path = config_path
            self.data = self.load_config()
        elif new_data:
            self.data = new_data
        else:
            raise ValueError("Either config_path or new_data must be provided")

    def load_config(self):
        with open(self.config_path, 'r') as file:
            return json.load(file)

    def parse_experiments(self) -> list:
        experiments = []
        objects = {}
        agents = {}
        arenas = {}
        try:
            environment = self.data['environment']
        except KeyError:
            raise ValueError("The 'environment' field is required")
        try:
            for k, v in environment['arenas'].items():
                if k.startswith('arena_'):
                    arenas.update({k:v})
                else: raise KeyError
        except KeyError:
            raise ValueError("The 'arenas' field is required with dictionary entries 'arena_#'")
        try:
            for k,v in environment['objects'].items():
                if k.startswith('static_') or k.startswith('movable_'):
                    objects.update({k:v}) 
                else: raise KeyError
        except KeyError:
            raise ValueError("The 'objects' field is required with dictionary entries 'static_#' or 'movable_#'")
        try:
            for k, v in environment['agents'].items():
                if k.startswith('static_') or k.startswith('movable_'):
                    agents.update({k: v})
                else: raise KeyError
        except KeyError:
            raise ValueError("The 'agents' field is required with dictionary entries 'static_#' or 'movable_#'")
        
        
        # Check required fields in agents
        num_experiments = None
        for agent in agents.values():
            if 'ticks_per_second' not in agent or 'number' not in agent:
                raise ValueError("Each agent must have 'ticks_per_second' and 'number' fields")
            if num_experiments is None:
                num_experiments = len(agent['number'])
            elif len(agent['number']) != num_experiments:
                raise ValueError("All agents must have the 'number' field with the same length")
            if len(agent['number']) == 0:
                raise ValueError("The 'number' field for agents must contain at least one element")
            for i in range(len(agent['number'])):
                if agent['number'][i] <= 0:
                    raise ValueError("The elements in the 'number' field for agents must be greater than 0")
        
        # Check required fields in objects
        # Check that all dictionaries in objects have the field 'number' with the same length
        for obj in objects.values():
            if '_id' not in obj or 'number' not in obj:
                raise ValueError("Each object must have '_id' and 'number' fields")
            if num_experiments is None:
                num_experiments = len(obj['number'])
            elif len(obj['number']) != num_experiments:
                raise ValueError("All objects must have the 'number' field with the same length")
        
        # Check required fields in arenas
        for arena in arenas.values():
            required_arena_fields = ["_id"]
            for field in required_arena_fields:
                if field not in arena:
                    raise ValueError(f"The '{field}' field is required in the arena")
                        
        # Check required fields in results
        if 'results' not in environment:
            raise ValueError("The 'results' field is required in the environment")
        required_results_fields = ["_id", "save"]
        for field in required_results_fields:
            if field not in environment['results']:
                raise ValueError(f"The '{field}' field is required in the results")
        
        # Check required fields in gui
        if 'gui' not in environment:
            raise ValueError("The 'gui' field is required in the environment")
        required_gui_fields = ["_id"]
        for field in required_gui_fields:
            if field not in environment['gui']:
                raise ValueError(f"The '{field}' field is required in the gui")
        
        for i in range(num_experiments):
            for arena_key, arena_value in arenas.items():
                required_fields = ["time_limit", "num_runs", "results", "gui", "render"]
                for field in required_fields:
                    if field not in environment:
                        raise ValueError(f"The '{field}' field is required in the environment")
                    else:
                        if field == "time_limit":
                            if not isinstance(environment[field], int) or environment[field] < 0:
                                raise ValueError(f"The '{field}' field must be a positive integer greater or equal to zero")
                        elif field == "num_runs":
                            if not isinstance(environment[field], int) or environment[field] <= 0:
                                raise ValueError(f"The '{field}' field must be a positive integer")
                        elif field == "render":
                            if not isinstance(environment[field], bool):
                                raise ValueError(f"The '{field}' field must be boolean")
                experiment = {
                    "environment": {
                        "parallel_experiments": environment.get("parallel_experiments",False),
                        "time_limit": environment.get("time_limit",500),
                        "num_runs": environment.get("num_runs",1),
                        "render": environment.get("render", False),
                        "results": environment.get("results"),
                        "gui": environment.get("gui"),
                        "arena": arena_value,
                        "objects": {},
                        "agents": {}
                    }
                }
            
                for obj_key, obj_value in objects.items():
                    experiment["environment"]["objects"][obj_key] = {**obj_value, "number": obj_value["number"][i]}
                for agent_key, agent_value in agents.items():
                    experiment["environment"]["agents"][agent_key] = {**agent_value, "number": agent_value["number"][i]}
                
                experiments.append(Config(new_data=experiment))
        
        return experiments

    @property
    def environment(self) -> dict:
        return self.data.get('environment', {})

    @property
    def arenas(self) -> dict:
        return self.data.get('environment', {}).get('arenas', {})

    @property
    def arena(self) -> dict:
        return self.data.get('environment', {}).get('arena', {})

    @property
    def objects(self) -> dict:
        return self.data.get('environment', {}).get('objects', {})

    @property
    def agents(self) -> dict:
        return self.data.get('environment', {}).get('agents', {})

    @property
    def results(self) -> dict:
        return self.data.get('environment', {}).get('results', {})

    @property
    def gui(self) -> dict:
        return self.data.get('environment', {}).get('gui', {})