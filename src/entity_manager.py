import gc, multiprocessing
from random import Random
from geometry_utils.vector3D import Vector3D

class EntityManager:
    def __init__(self,agents,arena_shape):
        self.agents = agents
        self.arena_shape = arena_shape

    def initialize(self,random_seed,object_shapes):
        for (config,entities) in self.agents.values():
            for n in range(len(entities)):
                entities[n].set_position(Vector3D(999,0,0),False)
        for (config,entities) in self.agents.values():
            for n in range(len(entities)):
                entities[n].set_random_generator(random_seed)
                if not entities[n].get_orientation_from_dict():
                    rand_angle = Random.uniform(entities[n].get_random_generator(),0.0,360.0)
                    entities[n].set_start_orientation(Vector3D(0,0,rand_angle))
                if not entities[n].get_position_from_dict():
                    count = 0
                    done = False
                    while not done and count < 500:
                        done = True
                        entities[n].to_origin()
                        min_v  = self.arena_shape.min_vert()
                        max_v  = self.arena_shape.max_vert()
                        rand_pos = Vector3D(Random.uniform(entities[n].get_random_generator(),min_v.x,max_v.x),
                                            Random.uniform(entities[n].get_random_generator(),min_v.y,max_v.y),
                                            abs(entities[n].get_shape().min_vert().z)) 
                        entities[n].set_position(rand_pos)
                        if entities[n].get_shape().check_overlap(self.arena_shape)[0]:
                            done = False
                        if done:
                            for m in range(len(entities)):
                                if m!=n and entities[n].get_shape().check_overlap(entities[m].get_shape())[0]:
                                    done = False
                                    break
                            for shapes in object_shapes.values():
                                for m in range(len(shapes)):
                                    if entities[n].get_shape().check_overlap(shapes[m])[0]:
                                        done = False
                                        break
                        count += 1
                        if done:
                            entities[n].set_start_position(rand_pos,False)
                    if not done:
                        raise Exception(f"Impossible to place agent {entities[n].entity()} in the arena")
                    
                else:
                    position = entities[n].get_start_position()
                    entities[n].set_start_position(Vector3D(position.x,position.y,position.z + (abs(entities[n].get_shape().min_vert().z))))
                entities[n].shape.translate_attachments(entities[n].orientation.z)

    def reset(self,object_shapes):
        for (config,entities) in self.agents.values():
            for n in range(len(entities)):
                entities[n].set_position(Vector3D(999,0,0),False)

        for (config,entities) in self.agents.values():
            for n in range(len(entities)):
                position = entities[n].get_start_position()
                entities[n].to_origin()
                if not entities[n].get_position_from_dict():
                    count = 0
                    done = False
                    while not done and count < 500:
                        done = True
                        min_v  = self.arena_shape.min_vert()
                        max_v  = self.arena_shape.max_vert()
                        rand_pos = Vector3D(Random.uniform(entities[n].get_random_generator(),min_v.x,max_v.x),
                                            Random.uniform(entities[n].get_random_generator(),min_v.y,max_v.y),
                                            abs(entities[n].get_shape().min_vert().z)) 
                        entities[n].to_origin()
                        entities[n].set_position(rand_pos)
                        if entities[n].get_shape().check_overlap(self.arena_shape)[0]:
                            done = False
                        if done:
                            for m in range(len(entities)):
                                if m!=n and entities[n].get_shape().check_overlap(entities[m].get_shape())[0]:
                                    done = False
                                    break
                            for shapes in object_shapes.values():
                                for m in range(len(shapes)):
                                    if entities[n].get_shape().check_overlap(shapes[m])[0]:
                                        done = False
                                        break
                        count += 1
                        if done: position = rand_pos
                    if not done:
                        raise Exception(f"Impossible to place agent {entities[n].entity()} in the arena")
                    entities[n].set_start_position(position,False)
                else:
                    entities[n].set_start_position(position)                    
                entities[n].set_start_orientation(entities[n].get_start_orientation())
                if not entities[n].get_orientation_from_dict():
                    rand_angle = Random.uniform(entities[n].get_random_generator(),0.0,360.0)
                    entities[n].set_start_orientation(Vector3D(0,0,rand_angle))
    def close(self,):
        pass

    def run(self,num_runs,time_limit, arena_queue:multiprocessing.Queue, agents_queue:multiprocessing.Queue, gui_out_queue: multiprocessing.Queue, render:bool=False):
        ticks_per_second = 1
        for (config,entities) in self.agents.values():
            ticks_per_second = entities[0].ticks()
            break
        ticks_limit = time_limit*ticks_per_second + 1 if time_limit > 0 else 0
        for run in range(1, num_runs + 1):
            while arena_queue.qsize() == 0: pass
            data_in = arena_queue.get()
            if data_in["status"][0]==0:
                self.initialize(data_in["random_seed"],data_in["objects_shapes"])
            agents_data = {
                "status": [0,ticks_per_second],
                "agents_shapes": self.get_agent_shapes()
            }
            agents_queue.put(agents_data)
            t = 1
            while True:
                while data_in["status"][0]/data_in["status"][1] < t/ticks_per_second:
                    if arena_queue.qsize()>0: data_in = arena_queue.get()
                    agents_data = {
                        "status": [t,ticks_per_second],
                        "agents_shapes": self.get_agent_shapes(),
                    }
                    if agents_queue.qsize() == 0: agents_queue.put(agents_data)
                if arena_queue.qsize()>0: data_in = arena_queue.get()
                for _,entities in self.agents.values():
                    for n in range(len(entities)):
                        entities[n].run(t,self.arena_shape,self.agents) # invoke the run method in a thread
                # print(f"agents_ticks {t} {ticks_per_second}")
                agents_data = {
                    "status": [t,ticks_per_second],
                    "agents_shapes": self.get_agent_shapes(),
                }
                agents_queue.put(agents_data)
                if render and gui_out_queue.qsize() > 0:
                    gui_data = gui_out_queue.get()
                    if gui_data["status"] == "end":
                        self.close()
                        break
                if ticks_limit > 0 and t >= ticks_limit: break
                t += 1
            if t < ticks_limit: break
            if run < num_runs:
                self.reset(data_in["objects_shapes"])
            else: self.close()
        gc.collect()

    def get_agent_positions(self) -> dict:
        positions = {}
        for _,entities in self.agents.values():
            temp = []
            for n in range(len(entities)):
                temp.append(entities[n].get_position())
            positions.update({entities[0].entity():temp})
        return positions

    def get_agent_orientations(self) -> dict:
        orientations = {}
        for _,entities in self.agents.values():
            temp = []
            for n in range(len(entities)):
                temp.append(entities[n].get_orientation())
            orientations.update({entities[0].entity():temp})
        return orientations

    def get_agent_shapes(self) -> dict:
        shapes = {}
        for _,entities in self.agents.values():
            temp = []
            for n in range(len(entities)):
                temp.append(entities[n].get_shape())
            shapes.update({entities[0].entity():temp})
        return shapes
    