from PySide6.QtWidgets import QApplication, QMainWindow, QToolBar, QPushButton, QWidget, QVBoxLayout
from PySide6.QtCore import Qt
from baseGUI import BaseGUI

class TwoDGUI(QMainWindow, BaseGUI):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("2D GUI")
        self.setGeometry(100, 100, 800, 600)

        # Create main widget and layout
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)

        # Create toolbar
        self.toolbar = QToolBar("Main Toolbar")
        self.addToolBar(Qt.TopToolBarArea, self.toolbar)

        # Add buttons to the toolbar
        self.add_toolbar_buttons()

        # Placeholder for the main screen where moving objects will be streamed
        self.main_screen = QWidget(self)
        self.main_screen.setStyleSheet("background-color: black;")
        self.layout.addWidget(self.main_screen)

    def add_toolbar_buttons(self):
        button_names = ["Button1", "Button2", "Button3", "Button4"]
        for name in button_names:
            button = QPushButton(name)
            self.toolbar.addWidget(button)

    def stream_moving_objects(self):
        # Placeholder method to stream moving objects
        pass

    @staticmethod
    def run():
        app = QApplication([])
        window = TwoDGUI()
        window.show()
        app.exec()