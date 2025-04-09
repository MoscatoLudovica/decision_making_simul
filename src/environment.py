import logging,multiprocessing,psutil
from config import Config
from entity import EntityFactory
from arena import ArenaFactory
from gui import GuiFactory
from entity_manager import EntityManager

class EnvironmentFactory():

    @staticmethod
    def create_environment(config_elem:Config):
        if not config_elem.environment["parallel_experiments"] or config_elem.environment["render"]:
            return SingleProcessEnvironment(config_elem)
        elif config_elem.environment["parallel_experiments"] and not config_elem.environment["render"]:
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
        return agents

    def run_gui(self, config, arena_vertices,gui_in_queue,gui_out_arena_queue,gui_out_agents_queue):
        """Function to run the GUI in a separate process"""
        app,gui = GuiFactory.create_gui(config,arena_vertices,gui_in_queue,gui_out_arena_queue,gui_out_agents_queue)
        gui.show()
        app.exec()

    def start(self):
        self.arena_shape="none"
        for exp in self.experiments:
            arena_queue = multiprocessing.Queue()
            agents_queue = multiprocessing.Queue()
            gui_in_queue = multiprocessing.Queue()
            gui_out_arena_queue = multiprocessing.Queue()
            gui_out_agents_queue = multiprocessing.Queue()
            arena = self.arena_init(exp)
            agents = self.agents_init(exp)
            entity_manager = EntityManager(agents,arena.get_shape())
            arena_process = multiprocessing.Process(target=arena.run, args=(self.num_runs,self.time_limit,arena_queue,agents_queue,gui_in_queue,gui_out_arena_queue,self.render[0]))
            agents_process = multiprocessing.Process(target=entity_manager.run, args=(self.num_runs,self.time_limit,arena_queue,agents_queue,gui_out_agents_queue,self.render[0]))
            agents_process.start()
            arena_process.start()
            # Initialize GUI only if rendering is enabled
            if self.render[0]:
                self.arena_shape = exp.arena.get("_id")
                self.render[1]["_id"] = "abstract" if self.arena_shape in (None, "none") else self.gui_id
                gui_process = multiprocessing.Process(target=self.run_gui, args=(self.render[1],arena.get_shape().vertices(),gui_in_queue,gui_out_arena_queue,gui_out_agents_queue))
                gui_process.start()
                killed = 0  
                while gui_process.is_alive():
                    if psutil.Process(gui_process.pid).status() == psutil.STATUS_ZOMBIE or psutil.Process(gui_process.pid).status() == psutil.STATUS_DEAD:
                        gui_out_arena_queue.put({"status": "end"})
                        gui_out_agents_queue.put({"status": "end"})
                        killed = 1
                        if arena_process.is_alive(): arena_process.terminate()
                        arena_process.join()
                        if agents_process.is_alive(): agents_process.terminate()
                        agents_process.join()
                        gui_process.terminate()
                        gui_process.join()
                    if self.auto_close_gui and not arena_process.is_alive():
                        arena_process.join()
                        if agents_process.is_alive(): agents_process.terminate()
                        agents_process.join()
                        gui_process.terminate()
                        gui_process.join()
                if killed == 1: break
            else:
                # Create and start the arena process
                arena_process.join()
                if agents_process.is_alive(): agents_process.terminate()
                agents_process.join()

        logging.info("All experiments completed successfully")

class MultiProcessEnvironment(Environment):
    
    def __init__(self,config_elem:Config):
        super().__init__(config_elem)
        logging.info("Multi process environment created successfully")

    def start(self):
        pass