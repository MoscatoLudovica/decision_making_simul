import logging
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
        self.random_seed = config_elem.arena.get("random_seed",-1)
        self._id = "none" if config_elem.arena.get("_id") == "abstract" else config_elem.arena.get("_id") 
        self.shape = None
        if self._id != "none":
            self.shape = Shape3DFactory.create_shape("arena",self._id, {key:val for key,val in config_elem.arena.items()})
        self.agents = {agent_type: (config_elem.environment.get("agents").get(agent_type),[]) for agent_type in config_elem.environment.get("agents").keys()}
        self.objects = {object_type: (config_elem.environment.get("objects").get(object_type),[]) for object_type in config_elem.environment.get("objects").keys()}
    
    def get_id(self):
        return self._id
    
    def get_shape(self):
        return self.shape
    
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
        pass

    def close(self):
        for (config,entities) in self.agents.values():
            for n in range(len(entities)):
                entities[n].close()
        for (config,entities) in self.objects.values():
            for n in range(len(entities)):
                entities[n].close()
        pass


class AbstractArena(Arena):
    
    def __init__(self, config_elem:Config):
        super().__init__(config_elem)
        logging.info("Abstract arena created successfully")
    
    def close(self):
        super().close()

class SolidArena(Arena):
    
    def __init__(self, config_elem:Config):
        super().__init__(config_elem)

    def initialize(self):
        super().initialize()
        # for (config,entities) in self.agents.values():
        #     for n in range(len(entities)):
        #         entities[n].set_position(Vector3D(999,0,0),False)
        # for (config,entities) in self.objects.values():
        #     for n in range(len(entities)):
        #         entities[n].set_position(Vector3D(999,0,0),False)
        # for (config,entities) in self.agents.values():
        #     for n in range(len(entities)):
        #         if entities[n].get_start_orientation() == None:
        #             rand_angle = Random.uniform(self.random_generator,0,360)
        #             entities[n].set_start_orientation(Vector3D(0,0,rand_angle))
        #         if entities[n].get_start_position() == None:
        #             count = 0
        #             done = False
        #             while not done and count < 200:
        #                 done = True
        #                 rand_pos = Vector3D(Random.uniform(self.random_generator,self.shape.min_vert_x(),self.shape.max_vert_x()),\
        #                                     Random.uniform(self.random_generator,self.shape.min_vert_y(),self.shape.max_vert_y()),\
        #                                     self.shape.floor + abs(entities[n].get_shape().min_vert_z())) 
        #                 entities[n].set_position(rand_pos)
        #                 if entities[n].get_shape().check_overlap(self.shape):
        #                     done = False
        #                 if done:
        #                     for m in range(len(entities)):
        #                         if m!=n and entities[n].get_shape().check_overlap(entities[m].get_shape()):
        #                             done = False
        #                             break
        #                 count += 1
        #                 if done:
        #                     entities[n].set_start_position(rand_pos)

        #         else:
        #             position = entities[n].get_start_position()
        #             print(position)
        #             print((entities[n].get_shape().min_vert_z()))
        #             entities[n].set_start_position(Vector3D(position.x,position.y,position.z + self.shape.floor + (abs(entities[n].get_shape().min_vert_z()))))
        #             print(entities[n].get_start_position())
        #             print((entities[n].get_shape().min_vert_z()))
                

        # for (config,entities) in self.objects.values():
        #     for n in range(len(entities)):
        #         if entities[n].get_start_orientation() == None:
        #             rand_angle = Random.uniform(self.random_generator,0,360)
        #             entities[n].set_start_orientation(Vector3D(0,0,rand_angle))
        #         if entities[n].get_start_position() == None:
        #             count = 0
        #             done = False
        #             while not done and count < 500:
        #                 done = True
        #                 rand_pos = Vector3D(Random.uniform(self.random_generator,self.shape.min_vert_x(),self.shape.max_vert_x()),\
        #                             Random.uniform(self.random_generator,self.shape.min_vert_y(),self.shape.max_vert_y()),\
        #                             self.shape.floor + abs(entities[n].get_shape().min_vert_z())) 
        #                 entities[n].set_position(rand_pos)
        #                 if entities[n].get_shape().check_overlap(self.shape):
        #                     done = False
        #                 if done:
        #                     for m in range(len(entities)):
        #                         if entities[n].get_shape_type() == "dense" and entities[m].get_shape_type()=="dense" and m!=n and entities[n].get_shape().check_overlap(entities[m].get_shape()):
        #                             done = False
        #                             break
        #                         if entities[n].get_shape_type() == "flat" and entities[m].get_shape_type()=="flat" and m!=n and entities[n].get_shape().check_overlap(entities[m].get_shape()):
        #                             done = False
        #                             break
        #                 if done and entities[n].get_shape_type() == "dense":
        #                     for (aconfig,aentities) in self.agents.values():
        #                         for an in range(len(aentities)):
        #                             if entities[n].get_shape().check_overlap(aentities[an].get_shape()):
        #                                 done = False
        #                                 break
        #                 count += 1
        #                 if done: entities[n].set_start_position(rand_pos)
        #         else:
        #             position = entities[n].get_start_position()
        #             entities[n].set_start_position(Vector3D(position.x,position.y,position.z + self.shape.floor + abs(entities[n].get_shape().min_vert_z())))
                

    def get_robot_positions(self) -> dict:
        positions = {}
        for _,entities in self.agents.values():
            temp = []
            for n in range(len(entities)):
                temp.append(entities[n].get_position())
            positions.update({entities[0].entity():temp})
        return positions
    
    def get_robot_orientations(self) -> dict:
        orientations = {}
        for _,entities in self.agents.values():
            temp = []
            for n in range(len(entities)):
                temp.append(entities[n].get_orientation())
            orientations.update({entities[0].entity():temp})
        return orientations
    
    def get_robot_shapes(self) -> dict:
        shapes = {}
        for _,entities in self.agents.values():
            temp = []
            for n in range(len(entities)):
                temp.append(entities[n].get_shape())
            shapes.update({entities[0].entity():temp})
        return shapes
    
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
    
    def run(self):
        super().run()
        
    def reset(self):
        super().reset()
        for (config,entities) in self.agents.values():
            for n in range(len(entities)):
                entities[n].set_position(Vector3D(999,0,0),False)
        for (config,entities) in self.objects.values():
            for n in range(len(entities)):
                entities[n].set_position(Vector3D(999,0,0),False)

        for (config,entities) in self.agents.values():
            for n in range(len(entities)):
                position = entities[n].get_start_position()
                if not entities[n].get_position_from_dict():
                    count = 0
                    done = False
                    while not done and count < 200:
                        done = True
                        rand_pos = Vector3D(Random.uniform(self.random_generator,self.shape.min_vert_x(),self.shape.max_vert_x()),\
                                    Random.uniform(self.random_generator,self.shape.min_vert_y(),self.shape.max_vert_y()),\
                                    self.shape.floor + abs(entities[n].get_shape().min_vert_z())) 
                        entities[n].set_position(rand_pos)
                        if entities[n].get_shape().check_overlap(self.shape):
                            done = False
                        if done:
                            for m in range(len(entities)):
                                if m!=n and entities[n].get_shape().check_overlap(entities[m].get_shape()):
                                    done = False
                                    break
                        count += 1
                        if done: position = rand_pos
                entities[n].set_start_position(position)
                entities[n].set_start_orientation(entities[n].get_start_orientation())
                if not entities[n].orientation_from_dict():
                    rand_angle = Random.uniform(self.random_generator,0,360)
                    entities[n].set_start_orientation(Vector3D(0,0,rand_angle))

        for (config,entities) in self.objects.values():
            for n in range(len(entities)):
                position = entities[n].get_start_position()
                if not entities[n].get_position_from_dict():
                    count = 0
                    done = False
                    while not done and count < 200:
                        done = True
                        rand_pos = Vector3D(Random.uniform(self.random_generator,self.shape.min_vert_x(),self.shape.max_vert_x()),\
                                    Random.uniform(self.random_generator,self.shape.min_vert_y(),self.shape.max_vert_y()),\
                                    self.shape.floor + abs(entities[n].get_shape().min_vert_z())) 
                        entities[n].set_position(rand_pos)
                        if entities[n].get_shape().check_overlap(self.shape):
                            done = False
                        if done:
                            for m in range(len(entities)):
                                if entities[n].get_shape_type() == "dense" and entities[m].get_shape_type()=="dense" and m!=n and entities[n].get_shape().check_overlap(entities[m].get_shape()):
                                    done = False
                                    break
                                if entities[n].get_shape_type() == "flat" and entities[m].get_shape_type()=="flat" and m!=n and entities[n].get_shape().check_overlap(entities[m].get_shape()):
                                    done = False
                                    break
                        if done and entities[n].get_shape_type() == "dense":
                            for (aconfig,aentities) in self.agents.values():
                                for an in range(len(aentities)):
                                    if entities[n].get_shape().check_overlap(aentities[an].get_shape()):
                                        done = False
                                        break
                        count += 1
                        if done: position = rand_pos
                entities[n].set_start_position(position)
                entities[n].set_start_orientation(entities[n].get_start_orientation())
                if not entities[n].orientation_from_dict():
                    rand_angle = Random.uniform(self.random_generator,0,360)
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
    