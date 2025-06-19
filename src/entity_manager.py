import multiprocessing as mp
from random import Random
from geometry_utils.vector3D import Vector3D

class EntityManager:
    def __init__(self, agents, arena_shape):
        self.agents = agents
        self.arena_shape = arena_shape

    def initialize(self, random_seed, objects):
        min_v = self.arena_shape.min_vert()
        max_v = self.arena_shape.max_vert()
        for (_, entities) in self.agents.values():
            for entity in entities:
                entity.set_position(Vector3D(999, 0, 0), False)
        for (config, entities) in self.agents.values():
            for entity in entities:
                entity.set_random_generator(config, random_seed)
                entity.reset()
                if not entity.get_orientation_from_dict():
                    rand_angle = Random.uniform(entity.get_random_generator(), 0.0, 360.0)
                    entity.set_start_orientation(Vector3D(0, 0, rand_angle))
                if not entity.get_position_from_dict():
                    count = 0
                    done = False
                    while not done and count < 500:
                        done = True
                        entity.to_origin()
                        rand_pos = Vector3D(
                            Random.uniform(entity.get_random_generator(), min_v.x, max_v.x),
                            Random.uniform(entity.get_random_generator(), min_v.y, max_v.y),
                            abs(entity.get_shape().min_vert().z)
                        )
                        entity.set_position(rand_pos)
                        shape_n = entity.get_shape()
                        # Check overlap with arena
                        if shape_n.check_overlap(self.arena_shape)[0]:
                            done = False
                        # Check overlap with other entities
                        if done:
                            for m, other_entity in enumerate(entities):
                                if other_entity is entity:
                                    continue
                                if shape_n.check_overlap(other_entity.get_shape())[0]:
                                    done = False
                                    break
                        # Check overlap with objects
                        if done:
                            for shapes, _, _, _ in objects.values():
                                for shape_obj in shapes:
                                    if shape_n.check_overlap(shape_obj)[0]:
                                        done = False
                                        break
                                if not done:
                                    break
                        count += 1
                        if done:
                            entity.set_start_position(rand_pos, False)
                    if not done:
                        raise Exception(f"Impossible to place agent {entity.entity()} in the arena")
                else:
                    entity.to_origin()
                    position = entity.get_start_position()
                    entity.set_start_position(Vector3D(position.x, position.y, abs(entity.get_shape().min_vert().z)))
                entity.shape.translate_attachments(entity.orientation.z)
                entity.spin_pre_run(objects)

    def close(self):
        pass

    def run(self, num_runs, time_limit, arena_queue: mp.Queue, agents_queue: mp.Queue, gui_out_queue: mp.Queue, dec_agents_in: mp.Queue, dec_agents_out: mp.Queue, render: bool = False):
        ticks_per_second = 1
        for (_, entities) in self.agents.values():
            ticks_per_second = entities[0].ticks()
            break
        ticks_limit = time_limit * ticks_per_second + 1 if time_limit > 0 else 0
        for run in range(1, num_runs + 1):
            while arena_queue.qsize() == 0:
                pass
            data_in = arena_queue.get()
            if data_in["status"][0] == 0:
                self.initialize(data_in["random_seed"], data_in["objects"])
            agents_data = {
                "status": [0, ticks_per_second],
                "agents_shapes": self.get_agent_shapes(),
                "agents_spins": self.get_agent_spins()
            }
            agents_queue.put(agents_data)
            t = 1
            while True:
                if ticks_limit > 0 and t >= ticks_limit:
                    break
                while data_in["status"][0] / data_in["status"][1] < t / ticks_per_second:
                    if arena_queue.qsize() > 0:
                        data_in = arena_queue.get()
                    agents_data = {
                        "status": [t, ticks_per_second],
                        "agents_shapes": self.get_agent_shapes(),
                        "agents_spins": self.get_agent_spins()
                    }
                    if agents_queue.qsize() == 0:
                        agents_queue.put(agents_data)
                if arena_queue.qsize() > 0:
                    data_in = arena_queue.get()
                for _, entities in self.agents.values():
                    for entity in entities:
                        entity.run(t, self.arena_shape, data_in["objects"])
                agents_data = {
                    "status": [t, ticks_per_second],
                    "agents_shapes": self.get_agent_shapes(),
                    "agents_spins": self.get_agent_spins()
                }
                detector_data = {
                    "agents": self.pack_detector_data()
                }
                agents_queue.put(agents_data)
                dec_agents_in.put(detector_data)
                dec_data_in = dec_agents_out.get()
                for _, entities in self.agents.values():
                    pos = dec_data_in.get(entities[0].entity())
                    if pos is not None:
                        for n, entity in enumerate(entities):
                            entity.post_step(pos[n])
                    else:
                        for entity in entities:
                            entity.post_step(None)
                if render and gui_out_queue.qsize() > 0:
                    gui_data = gui_out_queue.get()
                    if gui_data["status"] == "end":
                        self.close()
                        break
                t += 1
            if t < ticks_limit:
                break
            if run < num_runs:
                if arena_queue.qsize() > 0:
                    data_in = arena_queue.get()
            else:
                self.close()

    def pack_detector_data(self) -> dict:
        out = {}
        for _, entities in self.agents.values():
            shapes = [entity.get_shape() for entity in entities]
            velocities = [entity.get_max_absolute_velocity() for entity in entities]
            vectors = [entity.get_forward_vector() for entity in entities]
            positions = [entity.get_prev_position() for entity in entities]
            names = [entity.get_name() for entity in entities]
            out[entities[0].entity()] = (shapes, velocities, vectors, positions, names)
        return out

    def get_agent_shapes(self) -> dict:
        shapes = {}
        for _, entities in self.agents.values():
            shapes[entities[0].entity()] = [entity.get_shape() for entity in entities]
        return shapes

    def get_agent_spins(self) -> dict:
        spins = {}
        for _, entities in self.agents.values():
            spins[entities[0].entity()] = [entity.get_spin_system_data() for entity in entities]
        return spins