import multiprocessing as mp
from geometry_utils.vector3D import Vector3D

class CollisionDetector:
    def __init__(self, arena_shape, collisions):
        self.arena_shape = arena_shape
        self.collisions = collisions

    def run(self, dec_agents_in: mp.Queue, dec_agents_out: mp.Queue, dec_arena_in: mp.Queue):
        # Imposta su False per disattivare tutte le stampe di debug
        DEBUG_MODE = True
        
        self.agents, self.objects = {}, {}
        while True:
            out = {}
            if dec_arena_in.qsize() > 0:
                self.objects = dec_arena_in.get()["objects"]
            if dec_agents_in.qsize() > 0:
                self.agents = dec_agents_in.get()["agents"]
                for k, (shapes, velocities, vectors, positions, names) in self.agents.items():
                    n_shapes = len(shapes)
                    out_tmp = [None] * n_shapes
                    for n in range(n_shapes):
                        shape = shapes[n]
                        max_velocity = velocities[n]
                        forward_vector = vectors[n]
                        position = positions[n]
                        name = names[n]

                        # Inizializzazione delle variabili per accumulare le correzioni
                        collision_detected = False
                        total_velocity_projection = Vector3D()
                        total_separation_vector = Vector3D()
                        
                        # Lista per accumulare i messaggi di debug per questo agente in questo tick
                        debug_log = []

                        if self.collisions:
                            # --- Collisions with other agents ---
                            for dshapes, dvelocities, dvectors, dpositions, dnames in self.agents.values():
                                for m, dshape in enumerate(dshapes):
                                    dforward_vector, dposition, dname = dvectors[m], dpositions[m], dnames[m]
                                    if name == dname: continue
                                    
                                    delta = position - dposition
                                    sum_radius = shape.get_radius() + dshape.get_radius()
                                    if delta.magnitude() > sum_radius: continue
                                    
                                    overlap = shape.check_overlap(dshape)
                                    if overlap[0]:
                                        collision_detected = True
                                        velocity_projection = get_collision_normal(overlap[1], dshape, max_velocity) - forward_vector + dforward_vector
                                        total_velocity_projection += velocity_projection
                                        
                                        penetration_depth = sum_radius - delta.magnitude()
                                        if delta.magnitude() > 0:
                                            separation = delta.normalize() * penetration_depth * 0.1
                                            total_separation_vector += separation
                                            if DEBUG_MODE:
                                                debug_log.append(f"  - AGENT COLLISION with '{dname}':")
                                                debug_log.append(f"    - Velocity Proj.: {velocity_projection}")
                                                debug_log.append(f"    - Separation Vec.: {separation}")

                            # --- Collisions with objects ---
                            for dshapes, dpositions in self.objects.values():
                                for m, dshape in enumerate(dshapes):
                                    dposition = dpositions[m]
                                    delta = position - dposition
                                    sum_radius = shape.get_radius() + dshape.get_radius()
                                    if delta.magnitude() > sum_radius: continue
                                    
                                    overlap = shape.check_overlap(dshape)
                                    if overlap[0]:
                                        collision_detected = True
                                        velocity_projection = get_collision_normal(overlap[1], dshape, max_velocity) - forward_vector
                                        total_velocity_projection += velocity_projection
                                        
                                        penetration_depth = sum_radius - delta.magnitude()
                                        if delta.magnitude() > 0:
                                            separation = delta.normalize() * penetration_depth * 0.1
                                            total_separation_vector += separation
                                            if DEBUG_MODE:
                                                debug_log.append(f"  - OBJECT COLLISION at {dposition}:")
                                                debug_log.append(f"    - Velocity Proj.: {velocity_projection}")
                                                debug_log.append(f"    - Separation Vec.: {separation}")

                        # --- Collisions with arena borders ---
                        overlap = shape.check_overlap(self.arena_shape)
                        if overlap[0]:
                            collision_detected = True
                            velocity_projection = get_collision_normal(overlap[1], self.arena_shape, max_velocity) - forward_vector
                            total_velocity_projection += velocity_projection
                            
                            delta_arena = Vector3D(overlap[1].x, overlap[1].y, 0)
                            separation = delta_arena.normalize() * -0.01
                            total_separation_vector += separation
                            if DEBUG_MODE:
                                debug_log.append("  - ARENA BORDER COLLISION:")
                                debug_log.append(f"    - Velocity Proj.: {velocity_projection}")
                                debug_log.append(f"    - Separation Vec.: {separation}")

                        # --- Applica le correzioni e stampa il report di debug se necessario ---
                        if collision_detected:
                            final_position = position + total_velocity_projection + total_separation_vector
                            out_tmp[n] = final_position
                            
                            if DEBUG_MODE:
                                print(f"\n--- DEBUG: Collision Detected for Agent '{name}' ---")
                                print(f"Initial Position: {position}")
                                print(f"Initial Vector:   {forward_vector}")
                                # Stampa i dettagli delle singole collisioni
                                for log_entry in debug_log:
                                    print(log_entry)
                                print("-------------------------------------------------")
                                print(f"Total Velocity Projection: {total_velocity_projection}")
                                print(f"Total Separation Vector:   {total_separation_vector}")
                                print(f"FINAL Calculated Position: {final_position}")
                                print("-------------------------------------------------")
                        else:
                            out_tmp[n] = None

                    out[k] = out_tmp
                dec_agents_out.put(out)
    

def get_collision_normal(collision_point: Vector3D, shape, max_absolute_velocity: float) -> Vector3D:
    """
    Calcola il vettore normale di collisione in modo robusto.

    Per i cerchi, la normale è la linea dal centro al punto di collisione.
    Per le forme rettangolari (come l'arena), determina quale dei quattro lati
    è più vicino al punto di collisione e restituisce la normale perpendicolare
    a quel lato.

    Args:
        collision_point: Il punto in cui è stata rilevata la collisione.
        shape: La forma con cui è avvenuta la collisione (es. l'arena).
        max_absolute_velocity: La magnitudine da dare al vettore normale finale.

    Returns:
        Un Vector3D che rappresenta la normale di collisione, scalato dalla velocità.
    """
    # La logica per i cerchi è già robusta e corretta geometricamente
    if hasattr(shape, '_id') and shape._id == "circle":
        normal_vector = collision_point * -1
        return normal_vector.normalize() * max_absolute_velocity
    
    # Logica robusta per forme rettangolari/allineate agli assi (AABB)
    else:
        min_v = shape.min_vert()
        max_v = shape.max_vert()

        # Calcola la distanza del punto di collisione da ciascun lato dell'arena/oggetto
        distances = {
            'left':   abs(collision_point.x - min_v.x),
            'right':  abs(collision_point.x - max_v.x),
            'bottom': abs(collision_point.y - min_v.y),
            'top':    abs(collision_point.y - max_v.y)
        }

        # Trova il lato con la distanza minima. Questo è il lato della collisione.
        closest_wall = min(distances, key=distances.get)

        # Imposta la normale in base al lato più vicino
        # La normale punta sempre "lontano" dal muro per respingere l'oggetto
        normal = Vector3D(0, 0, 0)
        if closest_wall == 'left':
            normal.x = 1.0  # Spingi a destra
        elif closest_wall == 'right':
            normal.x = -1.0 # Spingi a sinistra
        elif closest_wall == 'bottom':
            normal.y = 1.0  # Spingi in alto
        elif closest_wall == 'top':
            normal.y = -1.0 # Spingi in basso
            
        # Scala la normale per la magnitudine desiderata e restituiscila
        return normal * max_absolute_velocity    
'''def get_collision_normal(collision_point: Vector3D, shape, max_absolute_velocity: float) -> Vector3D:
    if shape._id == "circle":
        normal_vector = collision_point * -1
        return normal_vector.normalize() * max_absolute_velocity
    else:
        min_v = shape.min_vert()
        max_v = shape.max_vert()
        tmp_x, tmp_y = 0, 0
        if collision_point.x <= min_v.x:
            tmp_x = max_absolute_velocity
        elif collision_point.x >= max_v.x:
            tmp_x = -max_absolute_velocity
        if collision_point.y <= min_v.y:
            tmp_y = max_absolute_velocity
        elif collision_point.y >= max_v.y:
            tmp_y = -max_absolute_velocity
        return Vector3D(tmp_x, tmp_y, 0)'''
