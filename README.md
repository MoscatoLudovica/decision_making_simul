# Decision Making Simulation Framework

This framework is designed to implement simulations for both single and multi-agent systems, with support for multiprocessing. It includes base classes to create a working arena where physical agents and/or objects can be deployed. Custom arenas can be built in the `arenas` folder. Additionally, there are base classes to provide a GUI, which can be switched off if not needed. Entities, which can be agents, objects, or highlighted areas in the arena, are also supported. A data handling class is provided to store data in a predefined format.

## Project Structure

- **arenas/**: Contains custom arenas where simulations take place. Users can create their own arenas by extending the base classes provided.
- **gui/**: Includes base classes for the graphical user interface. The GUI can be enabled or disabled based on user preference.
- **entities/**: Houses the definitions for various entities such as agents, objects, and highlighted areas within the arena.
- **data_handling/**: Provides classes and methods for storing and managing simulation data in a predefined format.

This structure allows for flexible and scalable simulation setups, catering to a wide range of research and development needs in decision-making processes.