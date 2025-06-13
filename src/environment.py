import logging,multiprocessing,psutil,gc
from config import Config
from entity import EntityFactory
from arena import ArenaFactory
from gui import GuiFactory
from entity_manager import EntityManager
from collision_detector import CollisionDetector

class EnvironmentFactory():

    @staticmethod
    def create_environment(config_elem:Config):
        if not config_elem.environment.get("parallel_experiments",False) or config_elem.environment["render"]:
            return SingleProcessEnvironment(config_elem)
        elif config_elem.environment.get("parallel_experiments",False) and not config_elem.environment["render"]:
            return MultiProcessEnvironment(config_elem)
        else:
            raise ValueError(f"Invalid environment configuration: {config_elem.environment['parallel_experiments']} {config_elem.environment['render']}")
        
class Environment():
    
    def __init__(self,config_elem:Config):
        self.experiments = config_elem.parse_experiments()
        self.num_runs = int(config_elem.environment.get("num_runs",1))
        self.time_limit = int(config_elem.environment.get("time_limit",0))
        self.gui_id = config_elem.gui.get("_id","2D")
        self.render = [config_elem.environment.get("render",False),config_elem.gui]
        self.auto_close_gui = config_elem.environment.get("auto_close_gui",True)
        self.collisions = config_elem.environment.get("collisions",True)

    def start(self):
        pass

class SingleProcessEnvironment(Environment):
    
    def __init__(self,config_elem:Config):
        super().__init__(config_elem)
        logging.info("Single process environment created successfully")

    def arena_init(self,exp):
        arena = ArenaFactory.create_arena(exp)
        if self.num_runs > 1 and arena.get_seed() < 0:
            arena.reset_seed()
        arena.initialize()
        return arena
    
    def agents_init(self,exp):
        agents = {agent_type: (exp.environment.get("agents").get(agent_type),[]) for agent_type in exp.environment.get("agents").keys()}
        for key,(config,entities) in agents.items():
            for n in range(config["number"]):
                entities.append(EntityFactory.create_entity(entity_type="agent_"+key,config_elem=config,_id=n))
        logging.info(f"Agents initialized: {list(agents.keys())}")
        return agents

    def run_gui(self, config, arena_vertices, arena_color,gui_in_queue,gui_control_queue):
        """Function to run the GUI in a separate process"""
        app,gui = GuiFactory.create_gui(config,arena_vertices,arena_color,gui_in_queue,gui_control_queue)
        gui.show()
        app.exec()

    def start(self):
        for exp in self.experiments:
            arena_queue = multiprocessing.Queue()
            agents_queue = multiprocessing.Queue()
            dec_arena_in = multiprocessing.Queue()
            dec_agents_in = multiprocessing.Queue()
            dec_agents_out = multiprocessing.Queue()
            gui_in_queue = multiprocessing.Queue()
            gui_out_arena_queue = multiprocessing.Queue()
            gui_out_agents_queue = multiprocessing.Queue()
            gui_control_queue = multiprocessing.Queue()
            arena = self.arena_init(exp)
            agents = self.agents_init(exp)
            collision_detector = CollisionDetector(arena.get_shape(),self.collisions)
            entity_manager = EntityManager(agents,arena.get_shape())
            arena_process = multiprocessing.Process(target=arena.run, args=(self.num_runs,self.time_limit,arena_queue,agents_queue,gui_in_queue,gui_out_arena_queue,dec_arena_in,gui_control_queue,self.render[0]))
            agents_process = multiprocessing.Process(target=entity_manager.run, args=(self.num_runs,self.time_limit,arena_queue,agents_queue,gui_out_agents_queue,dec_agents_in,dec_agents_out,self.render[0]))
            detector_process = multiprocessing.Process(target=collision_detector.run, args=(dec_agents_in,dec_agents_out,dec_arena_in))
            
            # Initialize GUI only if rendering is enabled
            killed = 0  
            if self.render[0]:
                self.render[1]["_id"] = "abstract" if arena.get_id() in (None, "none") else self.gui_id
                gui_process = multiprocessing.Process(target=self.run_gui, args=(self.render[1],arena.get_shape().vertices(),arena.get_shape().color(),gui_in_queue,gui_control_queue)) # type: ignore
                gui_process.start()
                if arena.get_id() not in ("abstract", "none", None): detector_process.start()
                agents_process.start()
                arena_process.start()
                while gui_process.is_alive():
                    if arena_process.exitcode not in (None, 0):
                        killed = 1
                        agents_process.terminate()
                        gui_process.terminate()
                        if detector_process.pid is not None:
                            if detector_process.is_alive(): detector_process.terminate()
                            detector_process.join()
                        arena_process.join()
                        agents_process.join()
                        gui_process.join()
                        raise RuntimeError(f"Arena process exited with code {arena_process.exitcode}")
                    elif agents_process.exitcode not in (None, 0):
                        killed = 1
                        arena_process.terminate()
                        gui_process.terminate()
                        if detector_process.pid is not None:
                            if detector_process.is_alive(): detector_process.terminate()
                            detector_process.join()
                        arena_process.join()
                        agents_process.join()
                        gui_process.join()
                        raise RuntimeError(f"Agents process exited with code {agents_process.exitcode}")
                    elif self.render[0] and gui_process.exitcode not in (None, 0):
                        killed = 1
                        arena_process.terminate()
                        agents_process.terminate()
                        if detector_process.pid is not None:
                            if detector_process.is_alive(): detector_process.terminate()
                            detector_process.join()
                        arena_process.join()
                        agents_process.join()
                        gui_process.join()
                        raise RuntimeError(f"GUI process exited with code {gui_process.exitcode}")
                    if psutil.Process(gui_process.pid).status() == psutil.STATUS_ZOMBIE or psutil.Process(gui_process.pid).status() == psutil.STATUS_DEAD:
                        gui_out_arena_queue.put({"status": "end"})
                        gui_out_agents_queue.put({"status": "end"})
                        killed = 1
                        if arena_process.is_alive(): arena_process.terminate()
                        arena_process.join()
                        if agents_process.is_alive(): agents_process.terminate()
                        agents_process.join()
                        if detector_process.pid is not None:
                            if detector_process.is_alive(): detector_process.terminate()
                            detector_process.join()
                        gui_process.terminate()
                        gui_process.join()
                    if self.auto_close_gui and not arena_process.is_alive():
                        arena_process.join()
                        agents_process.join()
                        if detector_process.pid is not None:
                            if detector_process.is_alive(): detector_process.terminate()
                            detector_process.join()
                        gui_process.terminate()
                        gui_process.join()
                if killed == 1: break
            else:
                if arena.get_id() not in ("abstract", "none", None): detector_process.start()
                agents_process.start()
                arena_process.start()

                while arena_process.exitcode==None and agents_process.exitcode==None:
                    pass
                
                if arena_process.exitcode not in (None, 0):
                    killed = 1
                    agents_process.terminate()
                    if detector_process.pid is not None:
                        if detector_process.is_alive(): detector_process.terminate()
                        detector_process.join()
                    arena_process.join()
                    agents_process.join()
                    raise RuntimeError(f"Arena process exited with code {arena_process.exitcode}")
                elif agents_process.exitcode not in (None, 0):
                    killed = 1
                    arena_process.terminate()
                    if detector_process.pid is not None:
                        if detector_process.is_alive(): detector_process.terminate()
                        detector_process.join()
                    arena_process.join()
                    agents_process.join()
                    raise RuntimeError(f"Agents process exited with code {agents_process.exitcode}")
                if killed == 0:
                    arena_process.join()
                    if agents_process.is_alive(): agents_process.terminate()
                    agents_process.join()
                    if detector_process.is_alive(): detector_process.terminate()
                    detector_process.join()
            gc.collect()
        logging.info("All experiments completed successfully")

class MultiProcessEnvironment(Environment):
    
    def __init__(self,config_elem:Config):
        super().__init__(config_elem)
        logging.info("Multi process environment created successfully")

    def start(self):
        pass