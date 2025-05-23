import logging, gc, multiprocessing
from config import Config
from random import Random
from bodies.shapes3D import Shape3DFactory
from entity import EntityFactory
from geometry_utils.vector3D import Vector3D

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
        self.ticks_per_second = config_elem.environment.get("ticks_per_second", 10)
        self.random_seed = config_elem.arena.get("random_seed",-1)
        self._id = "none" if config_elem.arena.get("_id") == "abstract" else config_elem.arena.get("_id","none") 
        self.objects = {object_type: (config_elem.environment.get("objects",{}).get(object_type),[]) for object_type in config_elem.environment.get("objects",{}).keys()}
        self.agents_shapes = {}

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
        self.set_random_seed()
        for key,(config,entities) in self.objects.items():
            for n in range(config["number"]):
                entities.append(EntityFactory.create_entity(entity_type="object_"+key,config_elem=config,_id=n))
                
    def run(self,num_runs,time_limit, arena_queue:multiprocessing.Queue, agents_queue:multiprocessing.Queue, gui_in_queue:multiprocessing.Queue, gui_out_queue:multiprocessing.Queue , render:bool=False):
        pass

    def reset(self):
        for (config,entities) in self.objects.values():
            for n in range(len(entities)):
                entities[n].reset()

    def close(self):
        for (config,entities) in self.objects.values():
            for n in range(len(entities)):
                entities[n].close()
        pass


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
        for (config,entities) in self.objects.values():
            for n in range(len(entities)):
                entities[n].set_position(Vector3D(999,0,0),False)
        for (config,entities) in self.objects.values():
            for n in range(len(entities)):
                if not entities[n].get_orientation_from_dict():
                    rand_angle = Random.uniform(self.random_generator,0.0,360.0)
                    entities[n].set_start_orientation(Vector3D(0,0,rand_angle))
                if not entities[n].get_position_from_dict():
                    count = 0
                    done = False
                    while not done and count < 500:
                        done = True
                        entities[n].to_origin()
                        min_v  = self.shape.min_vert()
                        max_v  = self.shape.max_vert()
                        rand_pos = Vector3D(Random.uniform(self.random_generator,min_v.x,max_v.x),
                                    Random.uniform(self.random_generator,min_v.y,max_v.y),
                                    abs(entities[n].get_shape().min_vert().z)) 
                        entities[n].set_position(rand_pos)
                        if entities[n].get_shape().check_overlap(self.shape)[0]:
                            done = False
                        if done:
                            for m in range(len(entities)):
                                if entities[n].get_shape_type() == "dense" and entities[m].get_shape_type()=="dense" and m!=n and entities[n].get_shape().check_overlap(entities[m].get_shape())[0]:
                                    done = False
                                    break
                                elif entities[n].get_shape_type() == "flat" and entities[m].get_shape_type()=="flat" and m!=n and entities[n].get_shape().check_overlap(entities[m].get_shape())[0]:
                                    done = False
                                    break
                        count += 1
                        if done: entities[n].set_start_position(rand_pos,False)
                    if not done:
                        raise Exception(f"Impossible to place object {entities[n].entity()} in the arena")
                else:
                    position = entities[n].get_start_position()
                    entities[n].set_start_position(Vector3D(position.x,position.y,position.z + abs(entities[n].get_shape().min_vert().z)))

    def get_object_positions(self) -> dict:
        positions = {}
        for _,entities in self.objects.values():
            temp = []
            for n in range(len(entities)):
                temp.append(entities[n].get_position())
            positions.update({entities[0].entity():temp})
        return positions
    
    def get_object_orientations(self) -> dict:
        orientations = {}
        for _,entities in self.objects.values():
            temp = []
            for n in range(len(entities)):
                temp.append(entities[n].get_orientation())
            orientations.update({entities[0].entity():temp})
        return orientations
    
    def get_object_shapes(self) -> dict:
        shapes = {}
        for _,entities in self.objects.values():
            temp = []
            for n in range(len(entities)):
                temp.append(entities[n].get_shape())
            shapes.update({entities[0].entity():temp})
        return shapes
    
    def run(self,num_runs,time_limit, arena_queue:multiprocessing.Queue, agents_queue:multiprocessing.Queue, gui_in_queue:multiprocessing.Queue, gui_out_queue:multiprocessing.Queue, render:bool=False):
        """Function to run the arena in a separate process"""
        ticks_limit = time_limit*self.ticks_per_second + 1 if time_limit > 0 else 0
        for run in range(1, num_runs + 1):
            logging.info(f"Run number {run} started")
            arena_data = {
                "status": [0,self.ticks_per_second],
                "objects_shapes": self.get_object_shapes(),
            }
            if render:
                gui_in_queue.put({**arena_data, "agents_shapes": self.agents_shapes})
            arena_queue.put({**arena_data, "random_seed": self.random_seed})
            while agents_queue.qsize() == 0: pass
            data_in = agents_queue.get()
            self.agents_shapes = data_in["agents_shapes"]
            t = 1
            while True:
                # print(f"arena_ticks {t} {self.ticks_per_second}")
                arena_data = {
                    "status": [t,self.ticks_per_second],
                    "objects_shapes": self.get_object_shapes(),
                }
                arena_queue.put(arena_data)
                while data_in["status"][0]/data_in["status"][1] < t/self.ticks_per_second:
                    if agents_queue.qsize()>0: data_in = agents_queue.get()
                    arena_data = {
                        "status": [t,self.ticks_per_second],
                        "objects_shapes": self.get_object_shapes(),
                    }
                    if arena_queue.qsize()==0: arena_queue.put(arena_data)
                if agents_queue.qsize()>0: data_in = agents_queue.get()
                self.agents_shapes = data_in["agents_shapes"]
                if render:
                    gui_in_queue.put({**arena_data, "agents_shapes": self.agents_shapes})
                    if gui_out_queue.qsize() > 0:
                        gui_data = gui_out_queue.get()
                        if gui_data["status"] == "end":
                            self.close()
                            break
                if ticks_limit > 0 and t >= ticks_limit: break
                t += 1
            if t < ticks_limit: break
            self.increment_seed()
            if run < num_runs:
                self.reset()
            else: self.close()
        gc.collect()
        
    def reset(self):
        super().reset()
        for (config,entities) in self.objects.values():
            for n in range(len(entities)):
                entities[n].set_position(Vector3D(999,0,0),False)
        for (config,entities) in self.objects.values():
            for n in range(len(entities)):
                position = entities[n].get_start_position()
                entities[n].to_origin()
                if not entities[n].get_position_from_dict():
                    count = 0
                    done = False
                    while not done and count < 500:
                        done = True
                        min_v  = self.shape.min_vert()
                        max_v  = self.shape.max_vert()
                        rand_pos = Vector3D(Random.uniform(self.random_generator,min_v.y,max_v.y),
                                    Random.uniform(self.random_generator,min_v.y,max_v.y),
                                    abs(entities[n].get_shape().min_vert().z)) 
                        entities[n].to_origin()
                        entities[n].set_position(rand_pos)
                        if entities[n].get_shape().check_overlap(self.shape)[0]:
                            done = False
                        if done:
                            for m in range(len(entities)):
                                if entities[n].get_shape_type() == "dense" and entities[m].get_shape_type()=="dense" and m!=n and entities[n].get_shape().check_overlap(entities[m].get_shape())[0]:
                                    done = False
                                    break
                                if entities[n].get_shape_type() == "flat" and entities[m].get_shape_type()=="flat" and m!=n and entities[n].get_shape().check_overlap(entities[m].get_shape())[0]:
                                    done = False
                                    break
                        if done and entities[n].get_shape_type() == "dense":
                            for (aconfig,aentities) in self.agents_shapes.values():
                                for an in range(len(aentities)):
                                    if entities[n].check_overlap(aentities[an].get_shape())[0]:
                                        done = False
                                        break
                        count += 1
                        if done: position = rand_pos
                    if not done:
                        raise Exception(f"Impossible to place object {entities[n].entity()} in the arena")
                    entities[n].set_start_position(position,False)
                else:
                    entities[n].set_start_position(position)                    
                entities[n].set_start_orientation(entities[n].get_start_orientation())
                if not entities[n].get_orientation_from_dict():
                    rand_angle = Random.uniform(self.random_generator,0.0,360.0)
                    entities[n].set_start_orientation(Vector3D(0,0,rand_angle))

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
    