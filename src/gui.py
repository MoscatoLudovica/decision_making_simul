import logging
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QGraphicsView, QGraphicsScene
from PySide6.QtCore import QTimer, Qt, QPointF
from PySide6.QtGui import QPolygonF, QColor, QPen, QBrush
class GuiFactory():

    @staticmethod
    def create_gui(config_elem:dict,queue):
        if config_elem.get("_id") in ("2D","abstract"):
            return QApplication([]),GUI_2D(config_elem,queue)
        elif config_elem.get("_id") == "3D":
            return GUI_3D(config_elem,queue)
        else:
            raise ValueError(f"Invalid gui type: {config_elem.gui['_id']} valid types are '2D' or '3D'")

class GUI_2D(QWidget):
    def __init__(self, config_elem: dict, queue):
        super().__init__()
        self._id = "2D"
        self.show_trajectories = config_elem.get("show_trajectories", False)
        self.show_communication = config_elem.get("show_communication", False)
        self.pixels_per_meter = config_elem.get("pixels_per_meter", 50)
        self.queue = queue
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
        self.timer.start(100)

        self.time = None
        self.arena_vertices = None
        self.robot_shapes = None
        self.object_shapes = None

        logging.info("2D GUI created successfully")

    def update_data(self):
        if not self.queue.empty():
            data = self.queue.get()
            self.time = data["time"]
            self.arena_vertices = data["arena_vertices"]
            self.robot_shapes = data["robot_shapes"]
            self.object_shapes = data["object_shapes"]
            self.update_scene()
            self.update()

    def update_scene(self):
        self.data_label.setText(f"Time: {self.time}")
        self.scene.clear()        
        if self.arena_vertices:
            polygon = QPolygonF([QPointF(v.x * self.pixels_per_meter, v.y * self.pixels_per_meter) for v in self.arena_vertices])
            arena_item = self.scene.addPolygon(polygon, QPen(Qt.black, 2), QBrush(QColor(200, 200, 200)))
            arena_item.setZValue(-1)

        if self.robot_shapes:
            self.scene.setBackgroundBrush(QColor(240, 240, 240))
            for key, robots_list in self.robot_shapes.items():
                for v in robots_list:
                    self.scene.addEllipse(
                        v.center.x * self.pixels_per_meter - 5, 
                        v.center.y * self.pixels_per_meter - 5, 
                        10, 10, QPen(Qt.blue), QBrush(Qt.blue))
        if self.object_shapes:
            for key, objects_list in self.object_shapes.items():
                for v in objects_list:
                    self.scene.addRect(
                        v.center.x * self.pixels_per_meter - 3, 
                        v.center.y * self.pixels_per_meter - 3, 
                        6, 6, QPen(Qt.red), QBrush(Qt.red))
        

class GUI_3D():

    def __init__(self,config_elem:dict,queue):
        if config_elem.get("_id") == "abstract":
            logging.info("Switching to 2D GUI")
            GUI_2D(config_elem,queue)
        else:
            self._id = "3D"
            logging.info("3D GUI created successfully")