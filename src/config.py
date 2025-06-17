import json
import itertools
import copy

class Config:
    def __init__(self, config_path: str = "", new_data: dict = {}):
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

    def _expand_entity(self, entity: dict, required_fields: list, optional_fields: list):
        """
        Espande tutte le combinazioni dei campi-lista di un'entità (agente o oggetto),
        ma NON fa il prodotto cartesiano sul campo 'position': se presente, viene sempre mantenuto intero.
        """
        # Controlli sui campi obbligatori
        for field in required_fields:
            if field not in entity:
                raise ValueError(f"Missing required field '{field}' in {entity.get('_id', 'entity')}")
        # Controlli di tipo
        for field in required_fields:
            if field == 'number':
                if not isinstance(entity[field], list):
                    raise ValueError(f"Field '{field}' must be a list in {entity.get('_id', 'entity')}")
                if len(entity[field]) == 0:
                    raise ValueError(f"Field '{field}' must not be empty in {entity.get('_id', 'entity')}")
                for n in entity[field]:
                    if not isinstance(n, int) or n <= 0:
                        raise ValueError(f"All elements in '{field}' must be positive integers in {entity.get('_id', 'entity')}")
        
        # Controllo specifico per il campo opzionale 'position'
        if 'position' in entity:
            pos = entity['position']
            if not (isinstance(pos, list) and all(isinstance(p, list) and len(p) in (2, 3) and all(isinstance(x, (int, float)) for x in p) for p in pos)):
                raise ValueError(f"Optional field 'position' must be a list of [x, y] o [x, y, z] arrays in {entity.get('_id', 'entity')}")

        # Trova tutti i campi-lista (sia obbligatori che opzionali), ESCLUDENDO 'position'
        list_fields = [f for f in required_fields + optional_fields if f in entity and isinstance(entity[f], list) and f != 'position']
        # Se nessun campo-lista (escluso position), restituisci l'entità così com'è
        if not list_fields:
            return [entity]
        # Prepara i valori per il prodotto cartesiano
        values = []
        for f in list_fields:
            v = entity[f]
            if not isinstance(v, list):
                v = [v]
            values.append(v)
        combinations = list(itertools.product(*values))
        expanded = []
        for combo in combinations:
            new_entity = copy.deepcopy(entity)
            for idx, f in enumerate(list_fields):
                new_entity[f] = combo[idx]
            # Per i campi-lista di lunghezza 1, sostituisci con il valore singolo
            for k in list_fields:
                if isinstance(entity[k], list) and len(entity[k]) == 1:
                    new_entity[k] = entity[k][0]
            # Il campo position viene sempre mantenuto intero, se presente
            expanded.append(new_entity)
        return expanded

    def parse_experiments(self) -> list:
        experiments = []
        objects = {}
        agents = {}
        arenas = {}
        try:
            environment = self.data['environment']
        except KeyError:
            raise ValueError("The 'environment' field is required")

        # Parsing e controlli su arenas
        try:
            for k, v in environment['arenas'].items():
                if k.startswith('arena_'):
                    if '_id' not in v:
                        raise ValueError("Each arena must have an '_id' field")
                    arenas.update({k: v})
                else:
                    raise KeyError
        except KeyError:
            raise ValueError("The 'arenas' field is required with dictionary entries 'arena_#'")

        # Parsing e controlli su objects
        object_required_fields = ['_id', 'number']
        object_optional_fields = [
            'strength', 'uncertainty','position'
        ]
        try:
            for k, v in environment['objects'].items():
                if k.startswith('static_') or k.startswith('movable_'):
                    objects[k] = self._expand_entity(v, object_required_fields, object_optional_fields)
                else:
                    raise KeyError
        except KeyError:
            raise ValueError("The 'objects' field is required with dictionary entries 'static_#' or 'movable_#'")

        # Parsing e controlli su agents
        agent_required_fields = ['ticks_per_second', 'number']
        agent_optional_fields = [
            'perception_width', 'num_groups', 'num_spins_per_group', 'perception_global_inhibition',
            'T', 'J', 'nu', 'p_spin_up', 'time_delay', 'dynamics','position'
        ]
        try:
            for k, v in environment['agents'].items():
                if k.startswith('static_') or k.startswith('movable_'):
                    agents[k] = self._expand_entity(v, agent_required_fields, agent_optional_fields)
                else:
                    raise KeyError
        except KeyError:
            raise ValueError("The 'agents' field is required with dictionary entries 'static_#' or 'movable_#'")

        if 'gui' not in environment:
            raise ValueError("The 'gui' field is required in the environment")
        if "_id" not in environment['gui']:
            raise ValueError("The '_id' field is required in the gui")

        agent_keys = list(agents.keys())
        object_keys = list(objects.keys())
        agent_combos = list(itertools.product(*[agents[k] for k in agent_keys])) if agent_keys else [()]
        object_combos = list(itertools.product(*[objects[k] for k in object_keys])) if object_keys else [()]

        for arena_key, arena_value in arenas.items():
            for agent_combo in agent_combos:
                for object_combo in object_combos:
                    experiment = {
                        "environment": {
                            "parallel_experiments": environment.get("parallel_experiments", False),
                            "time_limit": environment.get("time_limit", 500),
                            "num_runs": environment.get("num_runs", 1),
                            "render": environment.get("render", False),
                            "results": environment.get("results",{}),
                            "gui": environment.get("gui"),
                            "arena": arena_value,
                            "objects": {},
                            "agents": {}
                        }
                    }
                    for idx, agent_key in enumerate(agent_keys):
                        experiment["environment"]["agents"][agent_key] = agent_combo[idx] if agent_keys else {}
                    for idx, obj_key in enumerate(object_keys):
                        experiment["environment"]["objects"][obj_key] = object_combo[idx] if object_keys else {}
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