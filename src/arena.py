import logging
from config import Config
from random import Random
from bodies.shapes2D import Shape2DFactory
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
        self.ticks_per_second = config_elem.arena.get("ticks_per_second",10)
        self.random_seed = config_elem.arena.get("random_seed",-1)
        self._id = "none" if config_elem.arena.get("_id") == "abstract" else config_elem.arena.get("_id") 
        self.shape = Shape2DFactory.create_shape(self._id, {key:val for key,val in config_elem.arena.items()})
        self.agents = {agent_type: (config_elem.environment.get("agents").get(agent_type),[]) for agent_type in config_elem.environment.get("agents").keys()}
        self.objects = {object_type: (config_elem.environment.get("objects").get(object_type),[]) for object_type in config_elem.environment.get("objects").keys()}
    
    def get_id(self):
        return self._id
    
    def get_seed(self):
        return self.random_seed

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
        self.elapsed_ticks = 0
        self.set_random_seed()
        # agents initialization
        for key,(config,entities) in self.agents.items():
            for n in range(config["number"]):
                entities.append(EntityFactory.create_entity(entity_type="agent_"+key,config_elem=config,_id=n))
        # objects initialization
        for key,(config,entities) in self.objects.items():
            for n in range(config["number"]):
                entities.append(EntityFactory.create_entity(entity_type="object_"+key,config_elem=config,_id=n))

    def reset(self):
        for (config,entities) in self.agents.values():
            for n in range(len(entities)):
                entities[n].reset()
        for (config,entities) in self.objects.values():
            for n in range(len(entities)):
                entities[n].reset()

    def run(self):
        for _ in range(self.ticks_per_second):
            self.update()

    def update(self):
        self.elapsed_ticks += 1

    def close(self):
        # terminate threads and destroy entities
        pass


class AbstractArena(Arena):
    
    def __init__(self, config_elem:Config):
        super().__init__(config_elem)
        logging.info("Abstract arena created successfully")
    
    def update(self):
        super().update()
    
    def close(self):
        super().close()

class SolidArena(Arena):
    
    def __init__(self, config_elem:Config):
        super().__init__(config_elem)

    def initialize(self,x_low_bnd:float=0,x_high_bnd:float=1,y_low_bnd:float=0,y_high_bnd:float=1):
        super().initialize()
        for (config,entities) in self.agents.values():
            for n in range(len(entities)):
                rand_angle = Random.uniform(self.random_generator,a=0,b=360)
                rand_pos = Vector3D(Random.uniform(self.random_generator,x_low_bnd,x_high_bnd),Random.uniform(self.random_generator,y_low_bnd,y_high_bnd),0) 
                entities[n].set_angle(rand_angle)
                entities[n].set_start_position(rand_pos)
                count = 0
                done = True
                while not done and count+1 <= 200:
                    done = True
                    for m in range(len(entities)):
                        if m!=n and rand_pos == entities[m].get_position(): # check_overlap(args)
                            done = False
                            rand_pos = Vector3D(Random.uniform(self.random_generator,x_low_bnd,x_high_bnd),Random.uniform(self.random_generator,y_low_bnd,y_high_bnd),0) 
                            entities[n].set_start_position(rand_pos)
                            break

        for (config,entities) in self.objects.values():
            for n in range(len(entities)):
                rand_angle = Random.uniform(self.random_generator,a=0,b=360)
                rand_pos = Vector3D(Random.uniform(self.random_generator,x_low_bnd,x_high_bnd),Random.uniform(self.random_generator,y_low_bnd,y_high_bnd),0) 
                entities[n].set_angle(rand_angle)
                entities[n].set_start_position(rand_pos)
                count = 0
                done = True
                while not done and count+1 <= 200:
                    done = True
                    for m in range(len(entities)):
                        if entities[n].get_shape() == "dense" and entities[m].get_shape()=="dense" and m!=n and rand_pos == entities[m].get_position():
                            done = False
                            rand_pos = Vector3D(Random.uniform(self.random_generator,x_low_bnd,x_high_bnd),Random.uniform(self.random_generator,y_low_bnd,y_high_bnd),0) 
                            entities[n].set_start_position(rand_pos)
                            break
                        if entities[n].get_shape() == "flat" and entities[m].get_shape()=="flat" and m!=n and rand_pos == entities[m].get_position():
                            done = False
                            rand_pos = Vector3D(Random.uniform(self.random_generator,x_low_bnd,x_high_bnd),Random.uniform(self.random_generator,y_low_bnd,y_high_bnd),0) 
                            entities[n].set_start_position(rand_pos)
                            break
                    if entities[n].get_shape() == "dense" and done:
                        for (aconfig,aentities) in self.agents.values():
                            for an in range(len(aentities)):
                                if rand_pos == aentities[an].get_position():
                                    done = False
                                    rand_pos = Vector3D(Random.uniform(self.random_generator,x_low_bnd,x_high_bnd),Random.uniform(self.random_generator,y_low_bnd,y_high_bnd),0) 
                                    entities[n].set_start_position(rand_pos)
                                    break

    def get_robot_positions(self):
        positions = {}
        for _,entities in self.agents.values():
            temp = []
            for n in range(len(entities)):
                temp.append(entities[n].get_position())
            positions.update({entities[0].entity():temp})
        return positions
    
    def get_robot_angles(self):
        angles = {}
        for _,entities in self.agents.values():
            temp = []
            for n in range(len(entities)):
                temp.append(entities[n].get_angle())
            angles.update({entities[0].entity():temp})
        return angles
    
    def get_object_positions(self):
        positions = {}
        for _,entities in self.objects.values():
            temp = []
            for n in range(len(entities)):
                temp.append(entities[n].get_position())
            positions.update({entities[0].entity():temp})
        return positions
    
    def get_object_angles(self):
        angles = {}
        for _,entities in self.objects.values():
            temp = []
            for n in range(len(entities)):
                temp.append(entities[n].get_angle())
            angles.update({entities[0].entity():temp})
        return angles
    
    def update(self):
        super().update()
    
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
    