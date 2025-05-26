import multiprocessing
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
                                actual_distance = delta.magnitude()
                                if name != dname and actual_distance <= distance:
                                    overlap = shape.check_overlap(dshape)
                                    if overlap[0]:
                                        if correction == None: correction = position
                                        collision_normal = get_collision_normal(overlap[1], dshape, max_velocity)
                                        velocity_projection = collision_normal - forward_vector - collision_normal + dforward_vector
                                        penetration_depth = distance - actual_distance
                                        separation = delta.normalize() * penetration_depth*.1
                                        correction = correction + velocity_projection + separation
                        overlap = shape.check_overlap(self.arena_shape)
                        if overlap[0]:
                            if correction == None: correction = position
                            collision_normal = get_collision_normal(overlap[1],self.arena_shape,max_velocity)
                            velocity_projection = collision_normal - forward_vector
                            correction = correction + velocity_projection
                            shape.translate(correction)
                            overlap = shape.check_overlap(self.arena_shape)
                            if overlap[0]: correction = position + velocity_projection
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
        tmp_x, tmp_y = 0,0
        if collision_point.x <= min_v.x:
            tmp_x = max_absolute_velocity
        elif collision_point.x >= max_v.x:
            tmp_x = -max_absolute_velocity
        if collision_point.y <= min_v.y:
            tmp_y =  max_absolute_velocity
        elif collision_point.y >= max_v.y:
            tmp_y = -max_absolute_velocity
        return Vector3D(tmp_x, tmp_y, 0)
    