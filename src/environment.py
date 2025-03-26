import logging, gc, time
from config import Config
from arena import ArenaFactory
from gui import GuiFactory
import multiprocessing
import psutil

class EnvironmentFactory():

    @staticmethod
    def create_environment(config_elem:Config):
        if not config_elem.environment["multi_processing"] or config_elem.environment["render"]:
            return SingleProcessEnvironment(config_elem)
        elif config_elem.environment["multi_processing"] and not config_elem.environment["render"]:
            return MultiProcessEnvironment(config_elem)
        else:
            raise ValueError(f"Invalid environment configuration: {config_elem.environment['multi_processing']} {config_elem.environment['render']}")
        
class Environment():
    
    def __init__(self,config_elem:Config):
        self.experiments = config_elem.parse_experiments()
        self.num_runs = int(config_elem.environment.get("num_runs",1))
        self.time_limit = int(config_elem.environment.get("time_limit",0))
        self.gui_id = config_elem.gui.get("_id","2D")
        self.render = [config_elem.environment.get("render",False),config_elem.gui]
        self.gui = None
        self.arena = None

    def start(self):
        pass

class SingleProcessEnvironment(Environment):
    
    def __init__(self,config_elem:Config):
        super().__init__(config_elem)
        logging.info("Single process environment created successfully")

    def run_arena(self, exp, queue = None):
        """Function to run the arena in a separate process"""
        arena = ArenaFactory.create_arena(exp)
        if self.num_runs > 1 and arena.get_seed() < 0:
            arena.reset_seed()
        arena.initialize()
        for run in range(1, self.num_runs + 1):
            logging.info(f"Run number {run} started")
            t = 0
            data = {
                "time": t,
                "arena_vertices": arena.get_shape().vertices(),
                "robot_shapes": arena.get_robot_shapes(),
                "object_shapes": arena.get_object_shapes(),
            }
            # Send data to GUI
            if queue != None:
                queue.put(data)
            while True:
                t += 1
                arena.run()
                # Collect data from the arena
                data = {
                    "time": t,
                    "arena_vertices": arena.get_shape().vertices(),
                    "robot_shapes": arena.get_robot_shapes(),
                    "object_shapes": arena.get_object_shapes(),
                }
                # Send data to GUI
                if queue != None:
                    queue.put(data)
                if self.time_limit > 0 and t >= self.time_limit: break
            arena.increment_seed()
            if run < self.num_runs:
                if queue != None:
                    time.sleep(1)
                arena.reset()
            else: arena.close()
        gc.collect()

    def run_gui(self, config, queue):
        """Function to run the GUI in a separate process"""
        app,gui = GuiFactory.create_gui(config,queue)
        gui.show()
        app.exec()

    def start(self):
        self.arena_shape="none"
        for exp in self.experiments:
            # Initialize GUI only if rendering is enabled
            if self.render[0]:
                self.arena_shape = exp.arena.get("_id")
                self.render[1]["_id"] = "abstract" if self.arena_shape in (None, "none") else self.gui_id
                queue = multiprocessing.Queue()
                arena_process = multiprocessing.Process(target=self.run_arena, args=(exp,queue))
                gui_process = multiprocessing.Process(target=self.run_gui, args=(self.render[1],queue))
                gui_process.start()
                time.sleep(0.5)
                arena_process.start()
                time.sleep(0.5)
                killed = 0
                while queue.qsize()>0:
                    if psutil.Process(gui_process.pid).status() == psutil.STATUS_ZOMBIE:
                        killed = 1
                        gui_process.terminate()
                        gui_process.join()
                        arena_process.terminate()
                        arena_process.join()
                        break
                if killed == 0:
                    arena_process.join()
                    gui_process.terminate()
                    gui_process.join()

            else:
                # Create and start the arena process
                arena_process = multiprocessing.Process(target=self.run_arena, args=(exp,))
                arena_process.start()
                arena_process.join()

        logging.info("All experiments completed successfully")

class MultiProcessEnvironment(Environment):
    
    def __init__(self,config_elem:Config):
        super().__init__(config_elem)
        logging.info("Multi process environment created successfully")

    def start(self):
        pass