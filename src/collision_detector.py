import multiprocessing
import numpy as np
from geometry_utils.vector3D import Vector3D

class CollisionDetector:
    def __init__(self,arena_shape):
        self.arena_shape = arena_shape

    def run(self,dec_agents_in:multiprocessing.Queue,dec_agents_out:multiprocessing.Queue):
        agents = {}
        while True:
            if dec_agents_in.qsize() > 0:
                out = {}
                data = dec_agents_in.get()
                agents = data["agents"]
                for k,(shapes,velocities,vectors,positions,names) in agents.items():
                    out_tmp = [None]*len(shapes)
                    for n in range(len(shapes)):
                        shape = shapes[n]
                        max_velocity = velocities[n]
                        forward_vector = vectors[n]
                        position = positions[n]
                        name = names[n]
                        correction = None
                        for _,(dshapes,dvelocities,dvectors,dpositions,dnames) in agents.items():
                            for m in range(len(dshapes)):
                                dshape = dshapes[m]
                                # dmax_velocity = dvelocities[m]
                                dforward_vector = dvectors[m]
                                dposition = dpositions[m]
                                dname = dnames[m]
                                delta = Vector3D(position.x-dposition.x,position.y-dposition.y,0)
                                distance = shape.get_radius() + dshape.get_radius()
                                if name != dname and delta.magnitude()<=distance:
                                    overlap = shape.check_overlap(dshape)
                                    if overlap[0]:
                                        if correction == None: correction = position
                                        collision_normal = get_collision_normal(overlap[1], dshape, max_velocity)
                                        # Nuova logica: considera anche la velocità e direzione dell'altro agente
                                        correction = correction + collision_normal - forward_vector + dforward_vector

                        overlap = shape.check_overlap(self.arena_shape)
                        if overlap[0]:
                            if correction == None: correction = position
                            collision_normal = get_collision_normal(overlap[1],self.arena_shape,max_velocity)
                            velocity_projection = collision_normal - forward_vector
                            correction = correction + velocity_projection
                        if correction != None:
                            for _,(dshapes,dvelocities,dvectors,dpositions,dnames) in agents.items():
                                for m in range(len(dshapes)):
                                    dshape = dshapes[m] 
                                    dname = dnames[m]
                                    dposition = dpositions[m]
                                    delta = Vector3D(position.x-dposition.x,position.y-dposition.y,0)
                                    distance = shape.get_radius() + dshape.get_radius()
                                    if name != dname and delta.magnitude()<=distance:
                                        shape.translate(correction)
                                        overlap = shape.check_overlap(dshape)
                                        if overlap[0]: correction=position

                        out_tmp[n] = correction
                    out.update({k:out_tmp})
                dec_agents_out.put(out)

def get_collision_normal(collision_point:Vector3D,shape,max_absolute_velocity:float) -> Vector3D:
    if shape._id == "circle":
        normal_vector = collision_point*-1
        return normal_vector.normalize()*max_absolute_velocity
    else:
        min_v = shape.min_vert()
        max_v = shape.max_vert()
        if collision_point.x <= min_v.x:
            return Vector3D(max_absolute_velocity, 0, 0)
        elif collision_point.x >= max_v.x:
            return Vector3D(-max_absolute_velocity, 0, 0)
        elif collision_point.y <= min_v.y:
            return Vector3D(0, max_absolute_velocity, 0)
        elif collision_point.y >= max_v.y:
            return Vector3D(0, -max_absolute_velocity, 0)

    return Vector3D(0, 0, 0)
    