import logging
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QGraphicsView, QGraphicsScene
from PySide6.QtCore import QTimer, Qt, QPointF
from PySide6.QtGui import QPolygonF, QColor, QPen, QBrush
class GuiFactory():

    @staticmethod
    def create_gui(config_elem:dict,arena_vertices,arena_color,gui_in_queue):
        if config_elem.get("_id") in ("2D","abstract"):
            return QApplication([]),GUI_2D(config_elem,arena_vertices,arena_color,gui_in_queue)
        # elif config_elem.get("_id") == "3D":
        #     return GUI_3D(config_elem,arena_vertices,arena_color,gui_in_queue)
        else:
            raise ValueError(f"Invalid gui type: {config_elem.gui['_id']} valid types are '2D' or '3D'")

class GUI_2D(QWidget):
    def __init__(self, config_elem: dict,arena_vertices,arena_color,gui_in_queue):
        super().__init__()
        self._id = "2D"
        self.show_trajectories = config_elem.get("show_trajectories", False)
        self.show_communication = config_elem.get("show_communication", False)
        self.arena_vertices = arena_vertices
        self.arena_color = arena_color
        self.gui_in_queue = gui_in_queue
        self.setWindowTitle("Robot Arena GUI")

        self._layout = QVBoxLayout()
        self.data_label = QLabel("Waiting for data...")
        self._layout.addWidget(self.data_label)
        
        # Graphics View for arena visualization
        self.scale = 1
        self.view = QGraphicsView()
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0, 0, 800, 800)
        self.view.setScene(self.scene)
        self._layout.addWidget(self.view)
        self.setLayout(self._layout)

        # Timer to update GUI every 100ms
        self.timer = QTimer(self)
        self.connection = self.timer.timeout.connect(self.update_data)
        self.timer.start(1)
        self.time = None
        self.objects_shapes = None
        self.agents_shapes = None

        logging.info("2D GUI created successfully")

    def update_data(self):
        if self.gui_in_queue.qsize() > 0:
            data = self.gui_in_queue.get()
            self.time = data["status"][0]
            o_shapes = {}
            for k, item in data["objects"].items():
                o_shapes.update({k:item[0]})
            self.objects_shapes = o_shapes
            self.agents_shapes = data["agents_shapes"]
            # print(self.objects_shapes,'\n')
            # print('\n',self.agents_shapes)
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
        margin_x = 0.05
        margin_y = 0.05

        # Calculate the scaling factor to fit the arena within the drawing box
        scale_x = view_width / (arena_width + 2 * margin_x)
        scale_y = view_height / (arena_height + 2 * margin_y)
        self.scale = min(scale_x, scale_y)

        # Update pixels_per_meter to match the new scale

        # Center the arena in the drawing box
        offset_x = (view_width - (arena_width + 2 * margin_x) * self.scale) / 2
        offset_y = (view_height - (arena_height + 2 * margin_y) * self.scale) / 2

        # Store offsets for use with agents and objects
        self.offset_x = offset_x - (min_x - margin_x) * self.scale
        self.offset_y = offset_y - (min_y - margin_y) * self.scale

        # Transform the arena vertices
        transformed_vertices = [
            QPointF(
                v.x * self.scale + self.offset_x,
                v.y * self.scale + self.offset_y
            )
            for v in self.arena_vertices
        ]

        # Draw the transformed arena
        polygon = QPolygonF(transformed_vertices)
        self.scene.addPolygon(polygon, QPen(Qt.black, 2), QBrush(QColor(self.arena_color)))

    def update_scene(self):
        self.data_label.setText(f"Time: {self.time}")
        self.scene.clear()

        # Draw the arena
        self.draw_arena()

        if self.objects_shapes != None:
            self.scene.setBackgroundBrush(QColor(240, 240, 240))
            for key, entities in self.objects_shapes.items():
                for entity in entities:
                    entity_vertices = [
                        QPointF(
                            vertex.x * self.scale + self.offset_x,
                            vertex.y * self.scale + self.offset_y
                        )
                        for vertex in entity.vertices()
                    ]
                    entity_polygon = QPolygonF(entity_vertices)
                    entity_color = QColor(entity.color())
                    self.scene.addPolygon(entity_polygon, QPen(entity_color, .1), QBrush(entity_color))
        if self.agents_shapes != None:
            self.scene.setBackgroundBrush(QColor(240, 240, 240))
            for key, entities in self.agents_shapes.items():
                for entity in entities:
                    entity_vertices = [
                        QPointF(
                            vertex.x * self.scale + self.offset_x,
                            vertex.y * self.scale + self.offset_y
                        )
                        for vertex in entity.vertices()
                    ]
                    entity_polygon = QPolygonF(entity_vertices)
                    entity_color = QColor(entity.color())
                    self.scene.addPolygon(entity_polygon, QPen(entity_color, .1), QBrush(entity_color))
                    entity_attachments = entity.get_attachments()
                    for attachment in entity_attachments:
                        attachment_vertices = [
                            QPointF(
                                vertex.x * self.scale + self.offset_x,
                                vertex.y * self.scale + self.offset_y
                            )
                            for vertex in attachment.vertices()
                        ]
                        attachment_polygon = QPolygonF(attachment_vertices)
                        attachment_color = QColor(attachment.color())
                        self.scene.addPolygon(attachment_polygon, QPen(attachment_color, 1), QBrush(attachment_color))       

# class GUI_3D:

#     def __init__(self, config_elem: dict,arena_vertices,arena_color,gui_in_queue):
#         if config_elem.get("_id") == "abstract":
#             logging.info("Switching to 2D GUI")
#             GUI_2D(config_elem,arena_vertices,arena_color,gui_in_queue)
#         else:
#             self._id = "3D"
#             logging.info("3D GUI created successfully")