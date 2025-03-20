import logging, gc
from config import Config
from arena import ArenaFactory
from gui import GuiFactory
import multiprocessing

class EnvironmentFactory():

    @staticmethod
    def create_environment(config_elem:Config):
        if not config_elem.environment["multi_processing"] or config_elem.gui["render"]:
            return SingleProcessEnvironment(config_elem)
        elif config_elem.environment["multi_processing"] and not config_elem.gui["render"]:
            return MultiProcessEnvironment(config_elem)
        else:
            raise ValueError(f"Invalid environment configuration: {config_elem.environment['multi_processing']} {config_elem.gui['render']}")
        
class Environment():
    
    def __init__(self,config_elem:Config):
        self.experiments = config_elem.parse_experiments()
        self.num_runs = int(config_elem.environment.get("num_runs"))
        self.time_limit = int(config_elem.environment.get("time_limit"))
        self.gui_id = config_elem.gui.get("_id","2D")
        self.render = [config_elem.environment.get("render",False),config_elem.gui,True and config_elem.environment.get("render",False)]
        self.gui = None
        self.arena = None

    def start(self):
        pass

class SingleProcessEnvironment(Environment):
    
    def __init__(self,config_elem:Config):
        super().__init__(config_elem)
        logging.info("Single process environment created successfully")

    def run_arena(self, exp, queue):
        """Function to run the arena in a separate process"""
        arena = ArenaFactory.create_arena(exp)
        if self.num_runs > 1 and arena.get_seed() < 0:
            arena.reset_seed()
        arena.initialize()

        for run in range(1, self.num_runs + 1):
            logging.info(f"Run number {run} started")
            for t in range(self.time_limit):
                arena.run()
                # Collect data from the arena
                data = {
                    "time": t,
                    "robot_positions": arena.get_robot_positions(),  # Example function
                    "robot_angles": arena.get_robot_angles(),  # Example function
                    "object_positions": arena.get_object_positions(),  # Example function
                    "object_angles": arena.get_object_angles(),  # Example function
                }

                # Send data to GUI
                queue.put(data)
            arena.increment_seed()
            if run < self.num_runs:
                arena.reset()
        gc.collect()
        logging.info("Arena process completed")

    def run_gui(self, config, queue):
        """Function to run the GUI in a separate process"""
        app,gui = GuiFactory.create_gui(config,queue)
        gui.show()
        app.exec()
        # gui.run()  # Assuming GUI has a run method to start its event loop

    def start(self):
        self.arena_shape="none"
        for exp in self.experiments:
            # Create and start the arena process
            queue = multiprocessing.Queue()
            arena_process = multiprocessing.Process(target=self.run_arena, args=(exp,queue))
            arena_process.start()

            # Initialize GUI only if rendering is enabled
            if self.render[0]:
                new_arena_shape = exp.arena.get("_id")
                if self.arena_shape != new_arena_shape:
                    self.arena_shape = new_arena_shape
                    self.render[2] = True

                if self.render[2]:
                    self.render[1]["_id"] = "abstract" if self.arena_shape in (None, "none") else self.gui_id
                    gui_process = multiprocessing.Process(target=self.run_gui, args=(self.render[1],queue))
                    gui_process.start()
                    self.render[2] = False

                # Wait for both processes to finish
                arena_process.join()
                gui_process.join()
            else:
                arena_process.join()

        logging.info("All experiments completed successfully")

class MultiProcessEnvironment(Environment):
    
    def __init__(self,config_elem:Config):
        super().__init__(config_elem)
        logging.info("Multi process environment created successfully")

    def start(self):
        pass