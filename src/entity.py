import math, json, hashlib
import numpy as np
from random import Random
from geometry_utils.vector3D import Vector3D
from bodies.shapes3D import Shape3DFactory
from spinsystem import SpinSystem

_PI = math.pi
class EntityFactory:
    
    @staticmethod
    def create_entity(entity_type:str,config_elem: dict,_id:int=0):
        check_type = entity_type.split('_')[0]+'_'+entity_type.split('_')[1]
        if check_type == "agent_static":
            return StaticAgent(entity_type,config_elem,_id)
        elif check_type == "agent_movable":
            return MovableAgent(entity_type,config_elem,_id)
        elif check_type == "object_static":
            return StaticObject(entity_type,config_elem,_id)
        elif check_type == "object_movable":
            return MovableObject(entity_type,config_elem,_id)
        else:
            raise ValueError(f"Invalid agent type: {entity_type}")

class Entity:
    def __init__(self,entity_type:str, config_elem: dict,_id:int=0):
        self.entity_type = entity_type
        self._id = _id
        self.position_from_dict = False
        self.orientation_from_dict = False
        self.color = config_elem.get("color","black")
    
    def get_name(self):
        return self.entity_type+"_"+str(self._id)

    def get_position_from_dict(self):
        return self.position_from_dict
    
    def get_orientation_from_dict(self):
        return self.orientation_from_dict

    def reset(self):
        pass

    def entity(self) -> str:
        return self.entity_type
    
class Object(Entity):    
    def __init__(self,entity_type:str, config_elem: dict,_id:int=0):
        super().__init__(entity_type,config_elem,_id)
        if not config_elem.get("_id") in ("idle","interactive"):
            raise ValueError(f"Invalid object type: {self.entity_type}")

class Agent(Entity):
    def __init__(self, entity_type:str, config_elem:dict, _id:int=0):
        super().__init__(entity_type, config_elem, _id)
        self.random_generator = Random()
        self.ticks_per_second = config_elem.get("ticks_per_second", 31)
        self.color = config_elem.get("color", "blue")
        # --- messaging ---
        self.messages_config = config_elem.get("messages", {})
        self.msg_enable = True if len(self.messages_config) > 0 else False
        self.msg_comm_range = self.messages_config.get("comm_range", 0.1)
        self.msg_type = self.messages_config.get("type", "broadcast")
        self.msg_kind = self.messages_config.get("kind", "anonymous")
        self.msgs_per_sec = self.messages_config.get("messages_per_seconds", 1)
        self.msg_ticks_interval = max(1, int(self.ticks_per_second / self.msgs_per_sec))
        self.message_bus = None
        self.own_message = {}
        self.messages = []

    def set_message_bus(self, bus):
        self.message_bus = bus

    def should_send_message(self, tick):
        return self.msg_enable and ((tick - 1) % self.msg_ticks_interval == 0)

    def send_message(self,tick):
        if self.should_send_message(tick) and self.message_bus:
            self.own_message = {"tick":tick}
            self.message_bus.send_message(self, self.own_message)

    def receive_messages(self):
        if self.msg_enable and self.message_bus:
            messages = self.message_bus.receive_messages(self)
            if len(messages) > 0: self.messages.extend(messages)
            return messages
        return []
    
    def ticks(self): return self.ticks_per_second
    
    def set_random_generator(self,config,random_seed):
        config_str = json.dumps(config, sort_keys=True)
        config_seed = int(hashlib.sha256(config_str.encode()).hexdigest(), 16) % (2**32)
        seed = int(hashlib.sha256(f"{config_seed}_{random_seed}_{int(self.entity_type.split('_')[-1])}_{int(self._id)}".encode()).hexdigest(), 16) % (2**32)
        self.random_generator.seed(seed)

    def get_random_generator(self):
        return self.random_generator

    def run(self,tick,arena_shape,objects):
        pass

class StaticObject(Object):
    def __init__(self,entity_type:str, config_elem:dict,_id:int=0):
        super().__init__(entity_type,config_elem,_id)
        if config_elem.get("shape") in ("circle","square","rectangle"):
            self.shape_type = "flat"
        elif config_elem.get("shape") in ("sphere","cube","cuboid","cylinder"):
            self.shape_type = "dense"
        else: raise ValueError(f"Invalid object type: {self.entity_type}")
        self.shape = Shape3DFactory.create_shape("object",config_elem.get("shape","point"), {key:val for key,val in config_elem.items()})
        self.position = Vector3D()
        self.orientation = Vector3D()
        self.start_position = Vector3D()
        self.start_orientation = Vector3D()
        temp_strength = config_elem.get("strength", [10])
        if temp_strength != None:
            try:
                self.strength = temp_strength[_id]
            except:
                self.strength = temp_strength[-1]
        temp_uncertainty = config_elem.get("uncertainty", [0])
        if temp_uncertainty != None:
            try:
                self.uncertainty = temp_uncertainty[_id]
            except:
                self.uncertainty = temp_uncertainty[-1]
        temp_position = config_elem.get("position", None)
        if temp_position != None:
            self.position_from_dict = True
            try:
                self.start_position = Vector3D(temp_position[_id][0],temp_position[_id][1],temp_position[_id][2])
            except:
                self.start_position = Vector3D(temp_position[-1][0],temp_position[-1][1],temp_position[-1][2])
        temp_orientation = config_elem.get("orientation", None)
        if temp_orientation != None:
            self.orientation_from_dict = True
            try:
                self.start_orientation = Vector3D(temp_orientation[_id][0],temp_orientation[_id][1],temp_orientation[_id][2])
            except:
                self.start_orientation = Vector3D(temp_orientation[-1][0],temp_orientation[-1][1],temp_orientation[-1][2])
            self.orientation = self.start_orientation

    def to_origin(self):
        self.position = Vector3D()
        self.orientation = Vector3D()
        self.shape.center = self.position
        self.shape.set_vertices()

    def set_start_position(self,new_position:Vector3D,_translate:bool = True):
        self.start_position = new_position
        self.set_position(new_position,_translate)

    def set_position(self,new_position:Vector3D,_translate:bool = True):
        self.position = new_position
        if _translate: self.shape.translate(self.position)

    def set_start_orientation(self,new_orientation:Vector3D):
        self.start_orientation = new_orientation
        self.set_orientation(new_orientation)

    def set_orientation(self,new_orientation:Vector3D):
        self.orientation = new_orientation
        self.shape.rotate(self.start_orientation.z)

    def get_start_position(self):
        return self.start_position
    
    def get_start_orientation(self):
        return self.start_orientation
    
    def get_position(self):
        return self.position

    def get_orientation(self):
        return self.orientation
    
    def get_strength(self):
        return self.strength

    def get_uncertainty(self):
        return self.uncertainty
        
    def close(self):
        del self.shape

    def get_shape(self):
        return self.shape

    def get_shape_type(self):
        return self.shape_type
    
class StaticAgent(Agent):
    def __init__(self,entity_type:str, config_elem:dict,_id:int=0):
        super().__init__(entity_type,config_elem,_id)
        if config_elem.get("shape") in ("sphere","cube","cuboid","cylinder"):
            self.shape_type = "dense"
        else:
            # Aggiunto un fallback per evitare errori se la forma non è densa
            self.shape_type = "flat" 

        # --- INIZIO BLOCCO MODIFICATO ---

        # 1. Creiamo un dizionario pulito solo con i parametri per la forma
        # Questo evita di passare l'intero dizionario di configurazione dell'agente (che contiene liste)
        # alla factory della forma, che si aspetta valori singoli.
        shape_params = {
            "color": config_elem.get("color", "blue"),
            "diameter": config_elem.get("diameter"),
            "height": config_elem.get("height"),
            # Aggiungi qui altri parametri specifici della forma se ne hai (es. width, depth)
        }

        # 2. Creiamo la forma con i parametri puliti
        self.shape = Shape3DFactory.create_shape("agent", config_elem.get("shape", "point"), shape_params)
        self.shape.add_attachment(Shape3DFactory.create_shape("mark", "circle", {"_id": "idle", "color": "red", "diameter": 0.01}))

        # 3. Inizializziamo i vettori di posizione e orientamento
        self.position = Vector3D()
        self.orientation = Vector3D()
        self.start_position = Vector3D()
        self.start_orientation = Vector3D()

        # 4. Leggiamo la posizione dal dizionario, usando una logica robusta con _id
        temp_position = config_elem.get("position", None)
        if temp_position is not None:
            self.position_from_dict = True
            try:
                # Caso principale: una lista di posizioni. Prendi quella corrispondente al mio _id.
                pos_data = temp_position[_id]
                self.start_position = Vector3D(pos_data[0], pos_data[1], pos_data[2])
            except (IndexError, TypeError):
                # Caso di fallback:
                # 1. C'è una lista di posizioni ma _id è fuori range -> prendi l'ultima.
                # 2. C'è una sola posizione definita per tutti gli agenti (es. [[x,y,z]]).
                # 3. C'è una sola posizione definita come lista semplice (es. [x,y,z]).
                if isinstance(temp_position[0], list):
                    # È una lista di liste, prendi l'ultima come default
                    pos_data = temp_position[-1]
                else:
                    # È una singola lista [x, y, z]
                    pos_data = temp_position
                self.start_position = Vector3D(pos_data[0], pos_data[1], pos_data[2])

        # 5. Leggiamo l'orientamento (logica simile a quella della posizione)
        temp_orientation = config_elem.get("orientation", None)
        if temp_orientation is not None:
            self.orientation_from_dict = True
            try:
                # Caso principale: lista di orientamenti.
                orient_data = temp_orientation[_id]
                self.start_orientation = Vector3D(orient_data[0], orient_data[1], orient_data[2])
            except (IndexError, TypeError):
                # Caso di fallback.
                if isinstance(temp_orientation[0], list):
                    orient_data = temp_orientation[-1]
                else:
                    orient_data = temp_orientation
                self.start_orientation = Vector3D(orient_data[0], orient_data[1], orient_data[2])
            
            self.orientation = self.start_orientation

        # --- FINE BLOCCO MODIFICATO ---

    def to_origin(self):
        self.position = Vector3D()
        self.shape.center = self.position
        self.shape.set_vertices()

    def set_start_position(self,new_position:Vector3D,_translate:bool = True):
        self.start_position = new_position
        self.set_position(new_position,_translate)

    def set_position(self,new_position:Vector3D,_translate:bool = True):
        self.position = new_position
        if _translate:
            self.shape.translate(self.position)

    def set_start_orientation(self,new_orientation:Vector3D):
        self.start_orientation = new_orientation
        self.set_orientation(new_orientation)

    def set_orientation(self,new_orientation:Vector3D):
        self.orientation = new_orientation
        self.shape.rotate(self.start_orientation.z)

    def get_start_position(self):
        return self.start_position
    
    def get_start_orientation(self):
        return self.start_orientation
    
    def get_position(self):
        return self.position

    def get_orientation(self):
        return self.orientation

    def close(self):
        del self.shape

    def get_shape(self):
        return self.shape

    def get_shape_type(self):
        return self.shape_type
    
class MovableObject(StaticObject):
    def __init__(self,entity_type:str, config_elem:dict,_id:int=0):
        super().__init__(entity_type,config_elem,_id)

class MovableAgent(StaticAgent):

    STOP    = 0
    FORWARD = 1
    LEFT    = 2
    RIGHT   = 3

    def __init__(self,entity_type:str, config_elem:dict,_id:int=0):
        super().__init__(entity_type,config_elem,_id)
        self.config_elem = config_elem
        self.max_absolute_velocity = float(config_elem.get("linear_velocity",0.01)) / self.ticks_per_second
        self.max_angular_velocity = int(config_elem.get("angular_velocity",360)) / self.ticks_per_second
        self.forward_vector = Vector3D()
        self.goal_position = None
        self.prev_orientation = Vector3D()
        self.position = Vector3D()
        self.prev_position = Vector3D()
        self.prev_goal_distance = 0
        self.detection = config_elem.get("detection","GPS")
        self.moving_behavior = config_elem.get("moving_behavior","random_walk")
        self.pre_run = False


        # we define the number of bins of visual filed(angular resolution)
        self.num_visual_bins = config_elem.get("visual_bins",36)
        # dimension of agents
        self.agent_size = config_elem.get("agent_size",0.1)

        self.visual_mode = config_elem.get("visual_mode","binary")  # "binary" or "area"

        # coefficients from the paper (α0, α1, α2, β0, β1, β2, γ, v0)
        self.alpha0 = float(config_elem.get("alpha0", 0.5))
        self.alpha1 = float(config_elem.get("alpha1", 0.5))
        self.alpha2 = float(config_elem.get("alpha2", 0.0))
        self.beta0  = float(config_elem.get("beta0", 0.5))
        self.beta1  = float(config_elem.get("beta1", 0.5))
        self.beta2  = float(config_elem.get("beta2", 0.0))

        self.gamma = float(config_elem.get("gamma", 0.3))
        
        # prefered speed (in same units as self.max_absolute_velocity)
        self.v0_pref = float(config_elem.get("v0", self.max_absolute_velocity))

         # internal state for time derivative
        self.prev_visual_field = None

        # scalar speed (magnitude of forward vector) — gestito esplicitamente
        self.speed = self.forward_vector.magnitude() if hasattr(self,'forward_vector') else self.max_absolute_velocity




        if self.moving_behavior == "spin_model":
            self.spin_model_params = config_elem.get("spin_model", {})
            self.spin_pre_run_steps = self.spin_model_params.get("spin_pre_run_steps",0)
            self.pre_run = True if self.spin_pre_run_steps > 0 else False
            self.spin_per_tick = self.spin_model_params.get("spin_per_tick", 3)
            self.perception_width = self.spin_model_params.get("perception_width",0.5)
            self.num_groups = self.spin_model_params.get("num_groups",32)
            self.num_spins_per_group = self.spin_model_params.get("num_spins_per_group",10)
            self.perception_global_inhibition = self.spin_model_params.get("perception_global_inhibition",0)
            self.reference = self.spin_model_params.get("reference","egocentric")
            self.group_angles = np.linspace(0, 2 * _PI, self.num_groups, endpoint=False)
        elif self.moving_behavior == "vision":
            vm = config_elem.get("vision_model", {})
            self.visual_bins = vm.get("visual_bins", 72)
            self.body_length = vm.get("body_length", 0.1)
            self.visual_mode = vm.get("visual_mode", "binary")
        
            self.alpha0 = float(vm.get("alpha0", 1.0))
            self.alpha1 = float(vm.get("alpha1", 0.0))
            self.alpha2 = float(vm.get("alpha2", 0.0))
            self.beta0  = float(vm.get("beta0", 1.0))
            self.beta1  = float(vm.get("beta1", 0.0))
            self.beta2  = float(vm.get("beta2", 0.0))
            self.gamma  = float(vm.get("gamma", 1.0))
            self.v0_pref = float(vm.get("v0", self.max_absolute_velocity))
        
            self.prev_visual_field = None
            self.speed = self.max_absolute_velocity
        else:
            self.pre_run = False
            self.max_turning_ticks = 160
            self.standard_motion_steps = 5*16
            self.crw_exponent = config_elem.get("crw_exponent",1)
            self.levy_exponent = config_elem.get("levy_exponent",1.75)


    """ OUR PROJECT"""
    
    def build_visual_field(self, objects, all_entities):
        """
        Restituisce V(φ) discretizzato. Ora include sia oggetti che altri agenti.
        """
        N = self.visual_bins
        V = np.zeros(N, dtype=float)
        angles = np.linspace(-math.pi, math.pi, N, endpoint=False)
        bin_width = 2 * math.pi / N
        my_orient_rad = math.radians(self.orientation.z)
    
        # --- PRIMO LOOP: Processa gli OGGETTI STATICI (come prima) ---
        for _, (shapes, positions, strengths, uncertainties) in objects.items():
            for n in range(len(positions)):
                pos = positions[n]
                dx = pos.x - self.position.x
                dy = pos.y - self.position.y
                dist = math.hypot(dx, dy)
                angle_global = math.atan2(-dy, dx)
                rel_angle = ((angle_global - my_orient_rad) + math.pi) % (2 * math.pi) - math.pi
                BL = max(1e-6, self.body_length)
                if dist <= 1e-9: half_angle = math.pi
                else: half_angle = math.atan((BL / 2.0) / dist)
                for k, phi_k in enumerate(angles):
                    diff = abs(((phi_k - rel_angle + math.pi) % (2*math.pi)) - math.pi)
                    if diff <= half_angle:
                        if self.visual_mode == "binary": V[k] = 1.0
                        else: V[k] += 2.0 * half_angle
    
        # --- SECONDO LOOP: Processa gli ALTRI AGENTI (CORRETTO) ---
        for other_agent in all_entities:
            # Salta se l'entità sono io stesso
            if other_agent is self:
                continue
            
            pos = other_agent.get_position()
            dx = pos.x - self.position.x
            dy = pos.y - self.position.y
            dist = math.hypot(dx, dy)
    
            # Se un agente è troppo lontano, ignoralo per performance
            if dist > 2.0: # Puoi regolare questa "distanza di percezione"
                continue
    
            angle_global = math.atan2(-dy, dx)
            rel_angle = ((angle_global - my_orient_rad) + math.pi) % (2 * math.pi) - math.pi
            
            # Per la repulsione, usiamo il diametro fisico dell'agente per calcolare la sua dimensione apparente
            agent_diameter = self.shape.diameter if hasattr(self.shape, 'diameter') else 0.033
            BL = max(1e-6, agent_diameter)
            
            if dist <= 1e-9: half_angle = math.pi
            else: half_angle = math.atan((BL / 2.0) / dist)
    
            for k, phi_k in enumerate(angles):
                diff = abs(((phi_k - rel_angle + math.pi) % (2*math.pi)) - math.pi)
                if diff <= half_angle:
                    # Tratta gli altri agenti come ostacoli, quindi imposta V a 1.0
                    V[k] = 1.0
        
        if self.visual_mode == "binary":
            V = np.minimum(V, 1.0)
    
        return V, angles, bin_width
        
    
    def vision_routine(self, tick, arena_shape, objects, all_entities):
        """
        Implementazione discreta delle eq. (3) e (4) del paper.
        Output: aggiorna self.speed, self.orientation, self.forward_vector.
        """
        #print(f"TICK {tick}: Agente {self.get_name()} sta usando >>> VISION_ROUTINE <<<")
        
        # 1) costruisco V(φ)
        V, angles, bin_width = self.build_visual_field(objects, all_entities)  # V in [0,1] o area
        N = self.visual_bins
        dt = 1.0 / float(self.ticks_per_second)

        # 2) calcolo ∂φ V discretamente (gradient)
        dV_dphi = np.gradient(V, bin_width)   # ∂φ V (in unità di V per rad)

        # salvo per il passo successivo
        self.prev_visual_field = V.copy()

        # 4) costruisco integrandi per eq. (3) (accelerazione) e (4) (virata)
        # integrand_acc(φ) = cos(φ) * α0 * ( -V + α1*(∂φV)^2 + α2 * ∂tV )
        # integrand_turn(φ) = sin(φ) * β0 * ( -V + β1*(∂φV)^2 + β2 * ∂tV )
        # NOTA: α0 e β0 sono fattori esterni moltiplicativi (li applico dopo la somma)
        term_acc_inside = -V + self.alpha1 * (dV_dphi ** 2) 
        term_turn_inside = -V + self.beta1 * (dV_dphi ** 2)

        integrand_acc = np.cos(angles) * term_acc_inside
        integrand_turn = np.sin(angles) * term_turn_inside

        # 5) integra (somma) sul dominio φ
        integral_acc = np.sum(integrand_acc) * bin_width   # approssimazione dell'integrale su φ
        integral_turn = np.sum(integrand_turn) * bin_width

        # 6) applico α0 e β0 (come in eq.)
        vis_contrib_acc = self.alpha0 * integral_acc
        vis_contrib_turn = self.beta0 * integral_turn

        # 7) termine di rilassamento verso v0 (F_ind = γ (v0 - v))
        current_speed = self.speed
        relax_term = self.gamma * (self.v0_pref - current_speed)

        # 8) derivata della velocità scalare dv/dt
        dv_dt = relax_term + vis_contrib_acc

        # 9) derivata dell'angolo dψ/dt (in radianti al secondo)
        dpsi_dt = vis_contrib_turn

        # 10) integrazione esplicita (passo dt)
        new_speed = current_speed + dv_dt * dt
        new_speed = max(0.0, min(new_speed, self.max_absolute_velocity))
        # clamp speed >= 0, e (opzionale) <= qualche limite ragionevole
        # new_speed = max(0.0, new_speed)
        # max_allowed_speed = getattr(self, "max_speed", self.max_absolute_velocity * 3.0)
        #new_speed = min(new_speed, max_allowed_speed)
        
        self.speed = new_speed

        # 11) aggiorna orientazione (attenzione: orientation.z è in gradi nel tuo codice)
        delta_angle_deg = math.degrees(dpsi_dt * dt)   # dpsi_dt è rad/s -> moltiplico per dt -> rad -> converto in deg
        self.delta_orientation = Vector3D(0, 0, delta_angle_deg)
        self.orientation = self.orientation + self.delta_orientation
        self.orientation.z = normalize_angle(self.orientation.z)  # mantiene in [-180,180]

        # 12) aggiorna forward_vector coerente con speed e orientazione
        ang_rad = math.radians(self.orientation.z)
        scaling_factor = 1.0 
        self.forward_vector = (Vector3D(self.speed *scaling_factor* math.cos(ang_rad),self.speed *scaling_factor* -math.sin(ang_rad),0))
        print(self.forward_vector)

    def reset(self):
        if self.moving_behavior == "spin_model":
            self.perception = None
            self.spin_system = SpinSystem(
                self.random_generator,
                self.num_groups,
                self.num_spins_per_group,
                float(self.spin_model_params.get("T",0.1)),
                float(self.spin_model_params.get("J",1)),
                float(self.spin_model_params.get("nu",0)),
                float(self.spin_model_params.get("p_spin_up",0.5)),
                int(self.spin_model_params.get("time_delay",1)),
                self.spin_model_params.get("dynamics","metropolis")
            )
        else:
            self.turning_ticks = 0
            self.forward_ticks = 0
            self.motion = MovableAgent.STOP
            self.last_motion_tick = 0

    def get_spin_system_data(self):
        if self.moving_behavior == "spin_model":
            return self.spin_system.get_states(),self.spin_system.get_angles(),self.spin_system.get_external_field(),self.spin_system.get_avg_direction_of_activity()
        return None
    
    def get_max_absolute_velocity(self):
        return self.max_absolute_velocity
    
    def get_prev_position(self):
        return self.prev_position
    
    def get_prev_orientation(self):
        return self.prev_orientation
    
    def get_position(self):
        return self.position
    
    def get_orientation(self):
        return self.orientation
    
    def get_forward_vector(self):
        return self.forward_vector

    def set_start_orientation(self,new_orientation:Vector3D):
        super().set_start_orientation(new_orientation)
        
    def set_orientation(self,new_orientation:Vector3D):
        super().set_orientation(new_orientation)

    def random_walk(self,tick):
        if self.motion == MovableAgent.LEFT or self.motion == MovableAgent.RIGHT or self.motion == MovableAgent.STOP:
            if tick > self.last_motion_tick + self.turning_ticks:
                self.last_motion_tick = tick
                self.motion = MovableAgent.FORWARD
                self.forward_ticks = abs(levy(self.random_generator,self.standard_motion_steps,self.levy_exponent))
        elif self.motion == MovableAgent.FORWARD:
            if tick > self.last_motion_tick + self.forward_ticks:
                self.last_motion_tick = tick
                p = Random.uniform(self.random_generator,0,1)
                if p < 0.5: self.motion = MovableAgent.LEFT
                else: self.motion = MovableAgent.RIGHT
                angle = Random.uniform(self.random_generator,0,_PI) if self.crw_exponent == 0 else abs(wrapped_cauchy_pp(self.random_generator,self.crw_exponent))
                self.turning_ticks = int(angle * self.max_turning_ticks)

    def random_way_point(self, arena_shape):
        if self.goal_position is None or (self.position - self.goal_position).magnitude() <= .001:
            self.goal_position = self.shape._get_random_point_inside_shape(self.random_generator, arena_shape)
        dx = self.goal_position.x - self.position.x
        dy = self.goal_position.y - self.position.y
        angle_to_goal = math.degrees(math.atan2(-dy, dx))
        angle_to_goal = normalize_angle(angle_to_goal - self.orientation.z)
        distance = self.position - self.goal_position
        dist_mag = distance.magnitude()
        if abs(dist_mag) >= self.prev_goal_distance:
            self.last_motion_tick += 1
        self.prev_goal_distance = dist_mag
        if self.last_motion_tick > self.ticks_per_second:
            self.last_motion_tick = 0
            self.goal_position = None
        if angle_to_goal >= self.max_angular_velocity:
            self.motion = MovableAgent.LEFT
        elif angle_to_goal <= -self.max_angular_velocity:
            self.motion = MovableAgent.RIGHT
        else:
            self.motion = MovableAgent.FORWARD

    def post_step(self,position_correction):
        if position_correction != None:
            self.position = position_correction
            self.shape.translate(self.position)
            self.shape.translate_attachments(self.orientation.z)
    
    def spin_pre_run(self,objects):
        if self.pre_run:
            self.update_detection(objects)
            for _ in range(self.spin_pre_run_steps):
                self.spin_system.step(timedelay=False)
            self.spin_system.set_p_spin_up(np.mean(self.spin_system.get_states()))
            self.spin_system.reset_spins()

    def update_detection(self, objects):
        perception = np.zeros(self.num_groups * self.num_spins_per_group)
        sigma0 = self.perception_width
        for _, (shapes, positions, strengths, uncertainties) in objects.items():
            for n in range(len(shapes)):
                dx = positions[n].x - self.position.x
                dy = positions[n].y - self.position.y
                angle_to_object = math.degrees(math.atan2(-dy, dx))
                if self.reference == "egocentric":
                    angle_to_object = angle_to_object - self.orientation.z
                angle_to_object = normalize_angle(angle_to_object)
                effective_width = sigma0 + uncertainties[n]
                angle_diffs = np.abs(self.group_angles - math.radians(angle_to_object))
                angle_diffs = np.minimum(angle_diffs, 2 * _PI - angle_diffs)
                sigma = max(effective_width, 1e-6)
                weights = (sigma0 / sigma) * np.exp(-(angle_diffs ** 2) / (2 * (sigma ** 2)))
                weights *= strengths[n]
                perception += np.repeat(weights, self.num_spins_per_group)
        perception -= self.perception_global_inhibition
        self.perception = perception

    def run(self,tick,arena_shape,objects,all_entities):
        if self.detection == "visual":
            self.vision_routine(tick,arena_shape,objects,all_entities)
        elif self.detection == "GPS":
            self.GPS_routine(tick,arena_shape)
        dt = 1.0/self.ticks_per_second
        self.position = self.position + self.forward_vector*dt
        self.shape.rotate(self.delta_orientation.z)
        self.shape.translate(self.position)
        self.shape.translate_attachments(self.orientation.z)

    def spins_routine(self, objects):
        self.prev_position = self.position
        self.prev_orientation = self.orientation
        self.update_detection(objects)
        self.spin_system.update_external_field(self.perception)
        self.spin_system.run_spins(steps=self.spin_per_tick)
        angle_rad = self.spin_system.average_direction_of_activity()
        if angle_rad is not None:
            if self.reference == "allocentric":
                angle_rad = angle_rad - math.radians(self.orientation.z)
            angle_deg = normalize_angle(math.degrees(angle_rad))
            angle_deg = max(min(angle_deg, self.max_angular_velocity), -self.max_angular_velocity)
            self.delta_orientation = Vector3D(0, 0, angle_deg)
            self.orientation = self.orientation + self.delta_orientation
            self.orientation.z = normalize_angle(self.orientation.z)
            angle_rad = math.radians(self.orientation.z)
            width = self.spin_system.get_width_of_activity()
            scaling_factor = 1.0 / width if width and width > 0 else 0.0
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print(f"sto stampando width {width}")
            print(f"sto stampando scaling_factor {scaling_factor}")
            scaling_factor = np.clip(scaling_factor, 0.0, 1.0)
            cos_angle = math.cos(angle_rad)
            sin_angle = math.sin(angle_rad)
            self.forward_vector = Vector3D(
                self.max_absolute_velocity * scaling_factor * cos_angle,
                self.max_absolute_velocity * scaling_factor * -sin_angle,
                0
            )

    def GPS_routine(self, tick, arena_shape):
        print(f"TICK {tick}: Agente {self.get_name()} sta usando >>> GPS_ROUTINE <<<")
        if self.moving_behavior == "random_walk":
            self.random_walk(tick)
        elif self.moving_behavior == "random_way_point":
            self.random_way_point(arena_shape)
        else:
            raise ValueError(f"Invalid moving behavior: {self.moving_behavior}")
        self.prev_position = self.position
        self.prev_orientation = self.orientation
        self.delta_orientation = Vector3D(0, 0, 0)
        if self.motion == MovableAgent.LEFT:
            self.delta_orientation.z = self.max_angular_velocity
        elif self.motion == MovableAgent.RIGHT:
            self.delta_orientation.z = -self.max_angular_velocity
        self.orientation = self.orientation + self.delta_orientation
        self.orientation.z = normalize_angle(self.orientation.z)
        angle_rad = math.radians(self.orientation.z)
        cos_angle = math.cos(angle_rad)
        sin_angle = math.sin(angle_rad)
        self.forward_vector = Vector3D(
            self.max_absolute_velocity * cos_angle,
            self.max_absolute_velocity * -sin_angle,
            0
        )
    
    def close(self):
        return super().close()
    
def normalize_angle(angle: float):
    """Normalize the angle between -180 e 180 degrees."""
    return ((angle + 180) % 360) - 180

def exponential_distribution(random_generator, alpha):
    u = Random.uniform(random_generator, 0, 1)
    return -alpha * math.log1p(-u)

def wrapped_cauchy_pp(random_generator, c: float) -> float:
    q = 0.5
    u = Random.uniform(random_generator, 0, 1)
    val = (1 - c) / (1 + c)
    return 2 * math.atan(val * math.tanh(_PI * (u - q)))

def levy(random_generator, c: float, alpha: float) -> int:
    u = _PI * (Random.uniform(random_generator, 0, 1) - 0.5)
    if alpha == 1:
        return int(c * math.tan(u))
    v = 0
    while v == 0:
        v = exponential_distribution(random_generator, 1)
    if alpha == 2:
        return int(c * 2 * math.sin(u) * math.sqrt(v))
    t = math.sin(alpha * u) / math.pow(math.cos(u), 1 / alpha)
    s = math.pow(math.cos((1 - alpha) * u) / v, (1 - alpha) / alpha)
    return int(c * t * s)
