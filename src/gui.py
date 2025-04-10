import logging
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QGraphicsView, QGraphicsScene
from PySide6.QtCore import QTimer, Qt, QPointF
from PySide6.QtGui import QPolygonF, QColor, QPen, QBrush
class GuiFactory():

    @staticmethod
    def create_gui(config_elem:dict,arena_vertices,gui_in_queue,gui_out_arena_queue,gui_out_agents_queue):
        if config_elem.get("_id") in ("2D","abstract"):
            return QApplication([]),GUI_2D(config_elem,arena_vertices,gui_in_queue,gui_out_arena_queue,gui_out_agents_queue)
        # elif config_elem.get("_id") == "3D":
        #     return GUI_3D(config_elem,arena_vertices,gui_in_queue,gui_out_arena_queue,gui_out_agents_queue)
        else:
            raise ValueError(f"Invalid gui type: {config_elem.gui['_id']} valid types are '2D' or '3D'")

class GUI_2D(QWidget):
    def __init__(self, config_elem: dict,arena_vertices,gui_in_queue,gui_out_arena_queue,gui_out_agents_queue):
        super().__init__()
        self._id = "2D"
        self.show_trajectories = config_elem.get("show_trajectories", False)
        self.show_communication = config_elem.get("show_communication", False)
        self.pixels_per_meter = config_elem.get("pixels_per_meter", 50)
        self.arena_vertices = arena_vertices
        self.gui_in_queue = gui_in_queue
        self.gui_out_arena_queue = gui_out_arena_queue
        self.gui_out_agents_queue = gui_out_agents_queue
        self.setWindowTitle("Robot Arena GUI")

        self.layout = QVBoxLayout()
        self.data_label = QLabel("Waiting for data...")
        self.layout.addWidget(self.data_label)
        
        # Graphics View for arena visualization
        self.view = QGraphicsView()
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)
        self.layout.addWidget(self.view)
        self.setLayout(self.layout)

        # Timer to update GUI every 100ms
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_data)
        self.timer.start(1)

        self.time = None
        self.objects_shapes = None
        self.agents_shapes = None

        logging.info("2D GUI created successfully")

    def update_data(self):
        if not self.gui_in_queue.empty():
            data = self.gui_in_queue.get()
            self.time = data["status"][0]
            self.objects_shapes = data["objects_shapes"]
            self.agents_shapes = data["agents_shapes"]
        self.update_scene()
        self.update()

    def draw_arena(self):
        """Scale and center the arena vertices within the drawing box."""

        # Get the dimensions of the drawing box
        view_width = self.view.viewport().width()
        view_height = self.view.viewport().height()

        # Calculate the bounding box of the arena vertices
        min_x = min(v.x for v in self.arena_vertices)
        max_x = max(v.x for v in self.arena_vertices)
        min_y = min(v.y for v in self.arena_vertices)
        max_y = max(v.y for v in self.arena_vertices)

        # Calculate the arena width and height in meters
        arena_width = max_x - min_x
        arena_height = max_y - min_y

        # Add a margin (e.g., 10% of the arena size)
        margin_x = arena_width * 0.1
        margin_y = arena_height * 0.1

        # Calculate the scaling factor to fit the arena within the drawing box
        scale_x = view_width / ((arena_width + 2 * margin_x) * self.pixels_per_meter)
        scale_y = view_height / ((arena_height + 2 * margin_y) * self.pixels_per_meter)
        scale = min(scale_x, scale_y)

        # Update pixels_per_meter to match the new scale
        self.pixels_per_meter *= scale

        # Center the arena in the drawing box
        offset_x = (view_width - (arena_width + 2 * margin_x) * self.pixels_per_meter) / 2
        offset_y = (view_height - (arena_height + 2 * margin_y) * self.pixels_per_meter) / 2

        # Store offsets for use with agents and objects
        self.offset_x = offset_x - (min_x - margin_x) * self.pixels_per_meter
        self.offset_y = offset_y - (min_y - margin_y) * self.pixels_per_meter

        # Transform the arena vertices
        transformed_vertices = [
            QPointF(
                v.x * self.pixels_per_meter + self.offset_x,
                v.y * self.pixels_per_meter + self.offset_y
            )
            for v in self.arena_vertices
        ]

        # Draw the transformed arena
        polygon = QPolygonF(transformed_vertices)
        self.scene.addPolygon(polygon, QPen(Qt.black, 2), QBrush(QColor(200, 200, 200)))

    def update_scene(self):
        self.data_label.setText(f"Time: {self.time}")
        self.scene.clear()

        # Draw the arena
        self.draw_arena()

        # Draw agents
        if self.agents_shapes != None:
            self.scene.setBackgroundBrush(QColor(240, 240, 240))
            for key, entities in self.agents_shapes.items():
                for entity in entities:
                    # Draw the agent's vertices as a polygon
                    entity_vertices = [
                        QPointF(
                            vertex.x * self.pixels_per_meter + self.offset_x,
                            vertex.y * self.pixels_per_meter + self.offset_y
                        )
                        for vertex in entity.vertices()
                    ]
                    entity_polygon = QPolygonF(entity_vertices)
                    entity_color = QColor(entity.color())  # Use the agent's color
                    self.scene.addPolygon(entity_polygon, QPen(entity_color, 1), QBrush(entity_color))
        if self.objects_shapes != None:
            self.scene.setBackgroundBrush(QColor(240, 240, 240))
            for key, entities in self.objects_shapes.items():
                for entity in entities:
                    # Draw the agent's vertices as a polygon
                    entity_vertices = [
                        QPointF(
                            vertex.x * self.pixels_per_meter + self.offset_x,
                            vertex.y * self.pixels_per_meter + self.offset_y
                        )
                        for vertex in entity.vertices()
                    ]
                    entity_polygon = QPolygonF(entity_vertices)
                    entity_color = QColor(entity.color())  # Use the agent's color
                    self.scene.addPolygon(entity_polygon, QPen(entity_color, 1), QBrush(entity_color))

# class GUI_3D:

#     def __init__(self, config_elem: dict,arena_vertices,gui_in_queue,gui_out_arena_queue,gui_out_agents_queue):
#         if config_elem.get("_id") == "abstract":
#             logging.info("Switching to 2D GUI")
#             GUI_2D(config_elem,arena_vertices,gui_in_queue,gui_out_arena_queue,gui_out_agents_queue)
#         else:
#             self._id = "3D"
#             logging.info("3D GUI created successfully")