import logging, math
import matplotlib.pyplot as plt
from matplotlib.cm import coolwarm
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QGraphicsView, QGraphicsScene, QPushButton, QHBoxLayout
from PySide6.QtCore import QTimer, Qt, QPointF, QEvent
from PySide6.QtGui import QPolygonF, QColor, QPen, QBrush, QMouseEvent

class GuiFactory():

    @staticmethod
    def create_gui(config_elem:dict,arena_vertices,arena_color,gui_in_queue,gui_control_queue):
        if config_elem.get("_id") in ("2D","abstract"):
            return QApplication([]),GUI_2D(config_elem,arena_vertices,arena_color,gui_in_queue,gui_control_queue)
        else:
            raise ValueError(f"Invalid gui type: {config_elem.get('_id')} valid types are '2D' or '3D'")

class GUI_2D(QWidget):
    def __init__(self, config_elem: dict,arena_vertices,arena_color,gui_in_queue,gui_control_queue):
        super().__init__()
        self._id = "2D"
        self.on_click = config_elem.get("on_click", None)
        self.arena_vertices = arena_vertices
        self.arena_color = arena_color
        self.gui_in_queue = gui_in_queue
        self.gui_control_queue = gui_control_queue
        self.setWindowTitle("Arena GUI")

        # Layout principale orizzontale
        self._main_layout = QHBoxLayout()
        self._left_layout = QVBoxLayout()
        self.data_label = QLabel("Waiting for data...")
        self._left_layout.addWidget(self.data_label)
        self.button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")
        self.step_button = QPushButton("Step")
        self.button_layout.addWidget(self.start_button)
        self.button_layout.addWidget(self.stop_button)
        self.button_layout.addWidget(self.step_button)
        self._left_layout.addLayout(self.button_layout)
        self.start_button.clicked.connect(self.start_simulation)
        self.stop_button.clicked.connect(self.stop_simulation)
        self.step_button.clicked.connect(self.step_simulation)
        self.scale = 1
        self.view = QGraphicsView()
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0, 0, 800, 800)
        self.view.setScene(self.scene)
        
        self.clicked_spin = None
        self.canvas_visible = False
        if self.on_click == "show_spins":
            self.figure, self.ax = plt.subplots(subplot_kw={"projection": "polar"}, figsize=(4, 4))
            self.canvas = FigureCanvas(self.figure)

        self._left_layout.addWidget(self.view)
        self._main_layout.addLayout(self._left_layout)
        # La canvas viene aggiunta solo quando serve
        self.setLayout(self._main_layout)
        self.view.viewport().installEventFilter(self)
        self.resizeEvent(None)
        self.timer = QTimer(self)
        self.connection = self.timer.timeout.connect(self.update_data)
        self.timer.start(1)
        self.time = None
        self.objects_shapes = None
        self.agents_shapes = None
        self.agents_spins = None
        self.running = False
        self.step_requested = False
        logging.info("2D GUI created successfully")

    def eventFilter(self, watched, event):
        if watched == self.view.viewport() and event.type() == QEvent.Type.MouseButtonPress:
            mouse_event = event if isinstance(event, QMouseEvent) else None
            if mouse_event and mouse_event.button() == Qt.MouseButton.LeftButton:
                pos = mouse_event.pos()
                scene_pos = self.view.mapToScene(pos)
                self.clicked_spin = self.get_agent_at(scene_pos)
                if self.clicked_spin:
                    if not self.canvas_visible:
                        self._main_layout.addWidget(self.canvas)  # Mostra la canvas a destra
                        self.canvas_visible = True
                        self.update_spins_plot()
                    else:
                        self._main_layout.removeWidget(self.canvas)
                        self.canvas.setParent(None)
                        self.canvas_visible = False
            return True
        return super().eventFilter(watched, event)
    
    def get_agent_at(self, scene_pos):
        # Cerca un agente che contenga la posizione cliccata
        if self.agents_shapes is not None:
            for key , entities in self.agents_shapes.items():
                idx = 0
                for entity in entities:
                    polygon = QPolygonF([
                        QPointF(
                            vertex.x * self.scale + self.offset_x,
                            vertex.y * self.scale + self.offset_y
                        )
                        for vertex in entity.vertices()
                    ])
                    if polygon.containsPoint(scene_pos, Qt.FillRule.OddEvenFill): return key,idx
                    idx += 1
        return None
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        view_width = self.view.viewport().width()
        view_height = self.view.viewport().height()
        self.scene.setSceneRect(0, 0, view_width, view_height)
        self.scene.clear()
        self.draw_arena()

    def start_simulation(self):
        self.gui_control_queue.put("start")
        self.running = True

    def stop_simulation(self):
        self.gui_control_queue.put("stop")
        self.running = False

    def step_simulation(self):
        if not self.running:
            self.gui_control_queue.put("step")
            self.step_requested = True

    def update_spins_plot(self):
        self.ax.clear()
        if self.clicked_spin:
            spin = self.agents_spins.get(self.clicked_spin[0])[self.clicked_spin[1]]
            self.scene.setBackgroundBrush(QColor(240, 240, 240))
            group_mean_spins = spin[0].mean(axis=1)
            colors_spins = coolwarm((group_mean_spins))
            group_mean_perception = (
                spin[2].reshape(spin[1][1], spin[1][2]).mean(axis=1))
            normalized_perception = (group_mean_perception + 1) / 2
            colors_perception = coolwarm(normalized_perception)
            angles = spin[1][0][::spin[1][2]]
            self.ax.bar(
                angles,
                0.75,   # All bars have height=1
                width=2 * math.pi / spin[1][1],
                bottom=0.75,             # Shift ring inward
                color=colors_spins,
                edgecolor="black",
                alpha=0.9,
                #label="Spins",
            )
            avg_angle = spin[3]
            if avg_angle is not None:
                # Place an arrow near the inner ring
                self.ax.annotate(
                    "",
                    xy=(avg_angle, 0.5),   # End of the arrow
                    xytext=(avg_angle, 0.1),  # Start of the arrow
                    arrowprops=dict(facecolor="black", arrowstyle="->", lw=2),
                )
            self.ax.bar(
                angles,
                0.5,
                width=2 * math.pi / spin[1][1],
                bottom=1.6,
                color=colors_perception,
                edgecolor="black",
                alpha=0.9,
                label="Perception",
            )
            self.ax.set_yticklabels([])
            self.ax.set_xticks([])
            self.ax.grid(False)
        self.canvas.draw()

    def update_data(self):
        if self.running or self.step_requested:
            if self.gui_in_queue.qsize() > 0:
                data = self.gui_in_queue.get()
                self.time = data["status"][0]
                o_shapes = {}
                for k, item in data["objects"].items():
                    o_shapes.update({k:item[0]})
                self.objects_shapes = o_shapes
                self.agents_shapes = data["agents_shapes"]
                self.agents_spins = data["agents_spins"]
            self.update_scene()
            if self.on_click == "show_spins" and self.canvas_visible: self.update_spins_plot()
            self.update()
            if self.step_requested:
                self.step_requested = False

    def draw_arena(self):
        view_width = self.view.viewport().width()
        view_height = self.view.viewport().height()
        min_x = min(v.x for v in self.arena_vertices)
        min_y = min(v.y for v in self.arena_vertices)
        max_x = max(v.x for v in self.arena_vertices)
        max_y = max(v.y for v in self.arena_vertices)
        arena_width = max_x - min_x
        arena_height = max_y - min_y
        margin_x = 40
        margin_y = 40
        # keep the arena in the view
        scale_x = (view_width - 2*margin_x) / arena_width if arena_width > 0 else 1
        scale_y = (view_height - 2*margin_y) / arena_height if arena_height > 0 else 1
        self.scale = min(scale_x, scale_y)
        # Offset: top-left corner in (margin_x, margin_y)
        self.offset_x = margin_x - min_x * self.scale
        self.offset_y = margin_y - min_y * self.scale
        transformed_vertices = [
            QPointF(
                v.x * self.scale + self.offset_x,
                v.y * self.scale + self.offset_y
            )
            for v in self.arena_vertices
        ]
        polygon = QPolygonF(transformed_vertices)
        self.scene.addPolygon(polygon, QPen(Qt.black, 2), QBrush(QColor(self.arena_color)))

    def update_scene(self):
        self.data_label.setText(f"Time: {self.time}")
        self.scene.clear()
        self.draw_arena()
        if self.objects_shapes is not None:
            self.scene.setBackgroundBrush(QColor(240, 240, 240))
            for _, entities in self.objects_shapes.items():
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
        if self.agents_shapes is not None:
            self.scene.setBackgroundBrush(QColor(240, 240, 240))
            for _, entities in self.agents_shapes.items():
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
