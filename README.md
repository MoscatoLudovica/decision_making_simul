# Decision Making Simulation Framework

This framework is designed to implement simulations for both single and multi-agent systems, with support for multiprocessing. It includes base classes to create a working arena where physical agents and/or objects can be deployed. Custom arenas can be built in the `arenas` folder. Additionally, there are base classes to provide a GUI, which can be switched off if not needed. Entities, which can be agents, objects, or highlighted areas in the arena, are also supported. A data handling class is provided to store data in a predefined format.

## Project Structure

- **config/**: Provides the methods to handle the json configuration file.
- **environment/**: Manages the parallel processing of the siumulations.
- **arena/**: Contains custom arenas where simulations take place. Users can create their own arenas by extending the base classes provided.
- **entityManager/**: Manages the simulation of agents deployed in the arena.
- **entity/**: Houses the definitions for various entities such as agents, objects, and highlighted areas within the arena.
- **gui/**: Includes base classes for the graphical user interface. The GUI can be enabled or disabled based on user preference.
- **dataHandling/**: Provides classes and methods for storing and managing simulation data in a predefined format. It can be enabled or disabled based on user preference.

## Usage

After the first download the compile.sh file must be invoked. To give permissions open the terminal at the base folder level and type: sudo chmod +x *.sh. Then type ./compile.sh.
Now required packages from the requirements.txt file are installed in the virtual environment.

To run the simulations a run.sh file is provided.

## Config.json Example

```json
{
"environment":{
    "collisions": bool, DEFAULT:false
    "ticks_per_second": int, DEFAULT:10
    "time_limit": int, DEFAULT:0(inf)
    "num_runs": int, DEFAULT:1
    "results":{ DEFAULT:{} empty dict -> no saving. If rendering is enabled -> no saving
        "base_path": str, DEFAULT:"../data/" default saves results in a folder at the same level of .venv folder
        "model_specs": list(str) DEFAULT:None default saves only agents' position - *SUPPORTED:"spin_model"*
    },
    "gui":{ DEFAULT:{} empty dict -> no rendering
        "_id": "2D", Required
        "on_click": list(str) DEFAULT:None default shows nothing on click
    },
    "arenas":{ Required can define multiple arena to simulate sequentially
        "arena_0":{
            "random_seed": int, DEFAULT:random
            "width": int, DEFAULT:1
            "depth": int, DEFAULT:1
            "_id": str, Required - SUPPORTED:"rectangle","square","circle","abstract"
            "color": "gray" DEFAULT:white
        }
    },
    "objects":{ Required can define multiple objects to simulate in the same arena
        "static_0":{
            "number": list(int), DEFAULT:[1] each list's entry will define a different simulation
            "position": list(3Dvec), DEFAULT:None default assings random not-overlapping intial positions
            "orientation": list(3Dvec), DEFAULT:None default assings random intial orientations
            "_id": "str", Required - SUPPORTED:"idle","interactive"
            "shape": "str", Required - SUPPORTED:"circle","square","rectangle","sphere","cube","cylinder","none" flat geometry can be used to define walkable areas in the arena
            "height": float, DEFAULT:1 width and depth used for not-round objects
            "diameter": float, DEFAULT:1 used for round objects
            "color": "str", DEFAULT:"black"
            "strength": list(float), DEFAULT:[10] one entry -> assign to all the objects the same value. Less entries tha objects -> missing values are equal to the last one
            "uncertainty": list(float), DEFAULT:[0] one entry -> assign to all the objects the same value. Less entries tha objects -> missing values are equal to the last one
        }
    },
    "agents":{ Required can define multiple agents to simulate in the same arena
        "movable_0":{
            "ticks_per_second": int, DEFAULT:31
            "number": list(int), DEFAULT:[1] each list's entry will define a different simulation
            "position": list(3Dvec), DEFAULT:None default assings random not-overlapping intial positions
            "orientation": list(3Dvec), DEFAULT:None default assings random intial orientations
            "shape": str, - SUPPORTED:"sphere","cube","cylinder","none"
            "linear_velocity": float, DEFAULT:0.01 m/s
            "angular_velocity": float, DEFAULT:360 deg/s
            "height": float,
            "diameter": float,
            "color": str, DEFAULT:"blue"
            "detection": str, DEFAULT:"GPS" - SUPPORTED:"GPS","visual"
            "moving_behavior":str, DEFAULT:"random_walk" - SUPPORTED:"random_walk","random_way_point","spin_model". The last works only with visual detection
            "spin_model":{ DEFAULT:{} empty dict -> default configuration
                "spin_per_tick": int, DEFAULT:3
                "spin_pre_run_steps": int, DEFAULT:0 default value avoid pre run steps
                "perception_width": float, DEFAULT:0.5
                "num_groups": int, DEFAULT:32
                "num_spins_per_group": int, DEFAULT:10
                "perception_global_inhibition": int, DEFAULT:0
                "T": float, DEFAULT:0.5
                "J": float, DEFAULT:1
                "nu": float, DEFAULT:0
                "p_spin_up": float, DEFAULT:0.5
                "time_delay": int, DEFAULT:1
                "dynamics": "metropolis" DEFAULT:"metropolis"
            },
            "messages":{  DEFAULT:{} empty dict -> no messaging
                "messages_per_seconds": int, DEFAULT:1
                "comm_range": float, DEFAULT:0.1 m
                "type": str, DEFAULT:"broadcast"
                "kind": str DEFAULT:"anonymous"
            }
        }
    }
}
}
```
