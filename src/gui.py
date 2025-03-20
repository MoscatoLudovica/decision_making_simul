import logging
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import QTimer
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

    def __init__(self,config_elem:dict,queue):
        super().__init__()
        self._id = "2D"
        self.queue = queue
        self.setWindowTitle("Robot Arena GUI")
        self.layout = QVBoxLayout()
        self.data_label = QLabel("Waiting for data...")
        self.layout.addWidget(self.data_label)
        self.setLayout(self.layout)
        # Timer to update GUI every 100ms
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_data)
        self.timer.start(100)
        if config_elem.get("_id") == "abstract":
            pass
        else:
            pass
        logging.info("2D GUI created successfully")
        
    def update_data(self):
        if not self.queue.empty():
            data = self.queue.get()
            robots,objects = 0,0
            for key,entities in data['robot_positions'].items():
                robots += len(entities)
            for key,entities in data['object_positions'].items():
                objects += len(entities)
            self.data_label.setText(f"Time: {data['time']}, Robots: {robots}, Objects: {objects}")
class GUI_3D():

    def __init__(self,config_elem:dict,queue):
        if config_elem.get("_id") == "abstract":
            logging.info("Switching to 2D GUI")
            GUI_2D(config_elem,queue)
        else:
            self._id = "3D"
            logging.info("3D GUI created successfully")