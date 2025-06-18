import logging, multiprocessing, time
from config import Config
from random import Random
from bodies.shapes3D import Shape3DFactory
from entity import EntityFactory
from geometry_utils.vector3D import Vector3D
from dataHandling import DataHandlingFactory

class ArenaFactory():

    @staticmethod
    def create_arena(config_elem:Config):
        if config_elem.arena.get("_id") in ("abstract", "none", None):
            return AbstractArena(config_elem)
        elif config_elem.arena.get("_id") == "circle":
            return CircularArena(config_elem)
        elif config_elem.arena.get("_id") == "rectangle":
            return RectangularArena(config_elem)
        elif config_elem.arena.get("_id") == "square":
            return SquareArena(config_elem)
        else:
            raise ValueError(f"Invalid shape type: {config_elem.arena['_id']} valid types are: none, abstract, circle, rectangle, square")

class Arena():
    
    def __init__(self, config_elem:Config):
        self.random_generator = Random()
        self.ticks_per_second = int(config_elem.environment.get("ticks_per_second", 10))
        print(self.ticks_per_second)
        self.random_seed = config_elem.arena.get("random_seed",-1)
        self._id = "none" if config_elem.arena.get("_id") == "abstract" else config_elem.arena.get("_id","none") 
        self.objects = {object_type: (config_elem.environment.get("objects",{}).get(object_type),[]) for object_type in config_elem.environment.get("objects",{}).keys()}
        self.agents_shapes = {}
        self.agents_spins = {}
        self.data_handling = None
        if config_elem.results.get("save",False): self.data_handling = DataHandlingFactory.create_data_handling(config_elem)

    def get_id(self):
        return self._id
    
    def get_seed(self):
        return self.random_seed
    
    def get_random_generator(self):
        return self.random_generator

    def increment_seed(self):
        self.random_seed += 1
        
    def reset_seed(self):
        self.random_seed = 0
        
    def set_random_seed(self):
        if self.random_seed > -1:
            self.random_generator.seed(self.random_seed)
        else:
            self.random_generator.seed()

    def initialize(self):
        self.reset()
        for key,(config,entities) in self.objects.items():
            for n in range(config["number"]):
                entities.append(EntityFactory.create_entity(entity_type="object_"+key,config_elem=config,_id=n))
                
    def run(self,num_runs,time_limit, arena_queue:multiprocessing.Queue, agents_queue:multiprocessing.Queue, gui_in_queue:multiprocessing.Queue, gui_out_queue:multiprocessing.Queue ,dec_arena_in:multiprocessing.Queue, gui_control_queue:multiprocessing.Queue, render:bool=False):
        pass

    def reset(self):
        self.set_random_seed()

    def close(self):
        for (config,entities) in self.objects.values():
            for n in range(len(entities)):
                entities[n].close()
        if self.data_handling is not None: self.data_handling.close(self.agents_shapes)


class AbstractArena(Arena):
    
    def __init__(self, config_elem:Config):
        super().__init__(config_elem)
        logging.info("Abstract arena created successfully")
    
    def get_shape(self):
        pass
    
    def close(self):
        super().close()

class SolidArena(Arena):
    
    def __init__(self, config_elem:Config):
        super().__init__(config_elem)
        self.shape = Shape3DFactory.create_shape("arena",self._id, {key:val for key,val in config_elem.arena.items()})

    def get_shape(self):
        return self.shape
    
    def initialize(self):
        super().initialize()
        min_v = self.shape.min_vert()
        max_v = self.shape.max_vert()
        rng = self.random_generator
        for (config, entities) in self.objects.values():
            n_entities = len(entities)
            for entity in entities:
                entity.set_position(Vector3D(999, 0, 0), False)
            for n in range(n_entities):
                entity = entities[n]
                if not entity.get_orientation_from_dict():
                    rand_angle = Random.uniform(rng, 0.0, 360.0)
                    entity.set_start_orientation(Vector3D(0, 0, rand_angle))
                position = entity.get_start_position()
                if not entity.get_position_from_dict():
                    count = 0
                    done = False
                    shape_n = entity.get_shape()
                    shape_type_n = entity.get_shape_type()
                    min_vert_z = abs(shape_n.min_vert().z)
                    while not done and count < 500:
                        done = True
                        rand_pos = Vector3D(
                            Random.uniform(rng, min_v.x, max_v.x),
                            Random.uniform(rng, min_v.y, max_v.y),
                            min_vert_z
                        )
                        entity.to_origin()
                        entity.set_position(rand_pos)
                        shape_n = entity.get_shape()
                        # Overlap con arena
                        if shape_n.check_overlap(self.shape)[0]:
                            done = False
                        # Overlap con altre entità
                        if done:
                            for m in range(n_entities):
                                if m == n:
                                    continue
                                other_entity = entities[m]
                                other_shape = other_entity.get_shape()
                                other_shape_type = other_entity.get_shape_type()
                                if shape_type_n == other_shape_type and shape_n.check_overlap(other_shape)[0]:
                                    done = False
                                    break
                        count += 1
                        if done:
                            entity.set_start_position(rand_pos, False)
                    if not done:
                        raise Exception(f"Impossible to place object {entity.entity()} in the arena")
                else:
                    entity.to_origin()
                    entity.set_start_position(Vector3D(position.x, position.y, position.z + abs(entity.get_shape().min_vert().z)))

    def pack_objects_data(self) -> dict:
        out = {}
        for _,entities in self.objects.values():
            shapes = []
            positions = []
            strengths = []
            uncertainties = []
            for n in range(len(entities)):
                shapes.append(entities[n].get_shape())
                positions.append(entities[n].get_position())
                strengths.append(entities[n].get_strength())
                uncertainties.append(entities[n].get_uncertainty())
            out.update({entities[0].entity():(shapes,positions,strengths,uncertainties)})
        return out
    
    def pack_detector_data(self) -> dict:
        out = {}
        for _,entities in self.objects.values():
            shapes = []
            positions = []
            for n in range(len(entities)):
                shapes.append(entities[n].get_shape())
                positions.append(entities[n].get_position())
            out.update({entities[0].entity():(shapes,positions)})
        return out
        
    def run(self,num_runs,time_limit, arena_queue:multiprocessing.Queue, agents_queue:multiprocessing.Queue, gui_in_queue:multiprocessing.Queue, gui_out_queue:multiprocessing.Queue,dec_arena_in:multiprocessing.Queue, gui_control_queue:multiprocessing.Queue,render:bool=False):
        """Function to run the arena in a separate process"""
        ticks_limit = time_limit*self.ticks_per_second + 1 if time_limit > 0 else 0
        for run in range(1, num_runs + 1):
            logging.info(f"Run number {run} started")
            arena_data = {
                "status": [0,self.ticks_per_second],
                "objects": self.pack_objects_data()
            }
            if render:
                gui_in_queue.put({**arena_data, "agents_shapes": self.agents_shapes, "agents_spins": self.agents_spins})
            arena_queue.put({**arena_data, "random_seed": self.random_seed})

            while agents_queue.qsize() == 0: pass
            data_in = agents_queue.get()
            self.agents_shapes = data_in["agents_shapes"]
            self.agents_spins = data_in["agents_spins"]
            if self.data_handling is not None: self.data_handling.new_run(run,self.agents_shapes,self.agents_spins)
            t = 1
            running = False if render else True
            step_mode = False
            while True:
                if ticks_limit > 0 and t >= ticks_limit: break
                if render and gui_control_queue.qsize()>0:
                    cmd = gui_control_queue.get()
                    if cmd == "start":
                        running = True
                        step_mode = False
                    elif cmd == "stop":
                        running = False
                    elif cmd == "step":
                        step_mode = True
                        running = False
                arena_data = {
                    "status": [t,self.ticks_per_second],
                    "objects": self.pack_objects_data()
                }
                if running or step_mode:
                    if not render: print(f"\rarena_ticks {t}", end='', flush=True)
                    arena_queue.put(arena_data)
                    while data_in["status"][0]/data_in["status"][1] < t/self.ticks_per_second:
                        if agents_queue.qsize()>0: data_in = agents_queue.get()
                        arena_data = {
                            "status": [t,self.ticks_per_second],
                            "objects": self.pack_objects_data()
                        }
                        detector_data = {
                            "objects": self.pack_detector_data()
                        }
                        if arena_queue.qsize()==0:
                            arena_queue.put(arena_data)
                            dec_arena_in.put(detector_data)

                    if agents_queue.qsize()>0: data_in = agents_queue.get()
                    self.agents_shapes = data_in["agents_shapes"]
                    self.agents_spins = data_in["agents_spins"]
                    if self.data_handling is not None: self.data_handling.save(self.agents_shapes,self.agents_spins)
                    if render:
                        gui_in_queue.put({**arena_data, "agents_shapes": self.agents_shapes, "agents_spins": self.agents_spins})
                        if gui_out_queue.qsize() > 0:
                            gui_data = gui_out_queue.get()
                            if gui_data["status"] == "end":
                                self.close()
                                break
                    step_mode = False
                    t += 1
                else: time.sleep(0.05)
            if t < ticks_limit: break
            if run < num_runs:
                self.increment_seed()
                self.reset()
                if not render: print("")
            else:
                self.close()
                if not render: print("")
        
    def reset(self):
        super().reset()
        min_v = self.shape.min_vert()
        max_v = self.shape.max_vert()
        rng = self.random_generator
        if self.data_handling is not None: self.data_handling.close(self.agents_shapes)
        for (config, entities) in self.objects.values():
            n_entities = len(entities)
            for entity in entities:
                entity.set_position(Vector3D(999, 0, 0), False)
            for n in range(n_entities):
                entity = entities[n]
                entity.set_start_orientation(entity.get_start_orientation())
                if not entity.get_orientation_from_dict():
                    rand_angle = Random.uniform(rng, 0.0, 360.0)
                    entity.set_start_orientation(Vector3D(0, 0, rand_angle))
                position = entity.get_start_position()
                if not entity.get_position_from_dict():
                    count = 0
                    done = False
                    shape_n = entity.get_shape()
                    shape_type_n = entity.get_shape_type()
                    min_vert_z = abs(shape_n.min_vert().z)
                    while not done and count < 500:
                        done = True
                        rand_pos = Vector3D(
                            Random.uniform(rng, min_v.x, max_v.x),
                            Random.uniform(rng, min_v.y, max_v.y),
                            min_vert_z
                        )
                        entity.to_origin()
                        entity.set_position(rand_pos)
                        shape_n = entity.get_shape()
                        # Overlap con arena
                        if shape_n.check_overlap(self.shape)[0]:
                            done = False
                        # Overlap con altre entità
                        if done:
                            for m in range(n_entities):
                                if m == n:
                                    continue
                                other_entity = entities[m]
                                other_shape = other_entity.get_shape()
                                other_shape_type = other_entity.get_shape_type()
                                if shape_type_n == other_shape_type and shape_n.check_overlap(other_shape)[0]:
                                    done = False
                                    break
                        count += 1
                        if done:
                            entity.set_start_position(rand_pos, False)
                    if not done:
                        raise Exception(f"Impossible to place object {entity.entity()} in the arena")
                else:
                    entity.to_origin()
                    entity.set_start_position(Vector3D(position.x, position.y, position.z + abs(entity.get_shape().min_vert().z)))

    def close(self):
        super().close()

class CircularArena(SolidArena):
    
    def __init__(self, config_elem:Config):
        super().__init__(config_elem)
        self.height = config_elem.arena.get("height", 1)
        self.radius = config_elem.arena.get("radius", 1)
        self.color = config_elem.arena.get("color", "white")
        logging.info("Circular arena created successfully")
    

class RectangularArena(SolidArena):
    
    def __init__(self, config_elem:Config):
        super().__init__(config_elem)
        self.height = config_elem.arena.get("height", 1)
        self.length = config_elem.arena.get("length", 1)
        self.width = config_elem.arena.get("width", 1)
        self.color = config_elem.arena.get("color", "white")
        logging.info("Rectangular arena created successfully")
    
class SquareArena(SolidArena):
    
    def __init__(self, config_elem:Config):
        super().__init__(config_elem)
        self.height = config_elem.arena.get("height", 1)
        self.side = config_elem.arena.get("side", 1)
        self.color = config_elem.arena.get("color", "white")
        logging.info("Square arena created successfully")
    