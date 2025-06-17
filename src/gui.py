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
            raise ValueError(f"Invalid gui type: {config_elem.get('_id')} valid types are '2D' or 'abstract'")

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
        self.scene.setBackgroundBrush(QColor(240, 240, 240))
        self.view.setScene(self.scene)
        
        self.clicked_spin = None
        self.canvas_visible = False
        self.spins_bars = None
        self.perception_bars = None
        self.arrow = None
        self.angle_labels = []
        if self.on_click == "show_spins":
            self.figure, self.ax = plt.subplots(subplot_kw={"projection": "polar"}, figsize=(4, 4))
            self.canvas = FigureCanvas(self.figure)
            self.canvas.setMinimumSize(320, 320)
            self.canvas.setMaximumSize(320, 320)
        self._left_layout.addWidget(self.view)
        self._main_layout.addLayout(self._left_layout)
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
        logging.info("GUI created successfully")

    def eventFilter(self, watched, event):
        if event.type() == QEvent.Type.MouseButtonPress:
            if isinstance(event, QMouseEvent) and event.button() == Qt.MouseButton.LeftButton:
                pos = event.pos()
                scene_pos = self.view.mapToScene(pos)
                self.prev_clicked_spin = self.clicked_spin
                self.clicked_spin = self.get_agent_at(scene_pos)
                if self.clicked_spin:
                    if not self.canvas_visible or self.clicked_spin != self.prev_clicked_spin:
                        self._main_layout.addWidget(self.canvas)
                        self.canvas_visible = True
                    elif self.clicked_spin == self.prev_clicked_spin or self.clicked_spin == None:
                        self.clicked_spin = None
                        self._main_layout.removeWidget(self.canvas)
                        self.canvas.setParent(None)
                        self.canvas_visible = False
                else:
                    self._main_layout.removeWidget(self.canvas)
                    self.canvas.setParent(None)
                    self.canvas_visible = False
            return True
        return super().eventFilter(watched, event)
    
    def get_agent_at(self, scene_pos):
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
        if not (self.clicked_spin and self.agents_spins is not None):
            return
        spin = self.agents_spins.get(self.clicked_spin[0])[self.clicked_spin[1]]
        group_mean_spins = spin[0].mean(axis=1)
        colors_spins = coolwarm(group_mean_spins)
        group_mean_perception = spin[2].reshape(spin[1][1], spin[1][2]).mean(axis=1)
        normalized_perception = (group_mean_perception + 1) * 0.5
        colors_perception = coolwarm(normalized_perception)
        angles = spin[1][0][::spin[1][2]]
        width = 2 * math.pi / spin[1][1]
        if self.spins_bars is None or self.perception_bars is None:
            self.ax.clear()
            self.spins_bars = self.ax.bar(
                angles, 0.75, width=width, bottom=0.75,
                color=colors_spins, edgecolor="black", alpha=0.9
            )
            self.perception_bars = self.ax.bar(
                angles, 0.5, width=width, bottom=1.6,
                color=colors_perception, edgecolor="black", alpha=0.9
            )
            self.angle_labels = []
            for deg, label in zip([0, 90, 180, 270], ["0°", "90°", "180°", "270°"]):
                rad = math.radians(deg)
                txt = self.ax.text(rad, 2.5, label, ha="center", va="center", fontsize=10)
                self.angle_labels.append(txt)
            self.ax.set_yticklabels([])
            self.ax.set_xticks([])
            self.ax.grid(False)
        else:
            for bar, color in zip(self.spins_bars, colors_spins):
                bar.set_color(color)
            for bar, color in zip(self.perception_bars, colors_perception):
                bar.set_color(color)
        avg_angle = spin[3]
        if avg_angle is not None:
            if self.arrow is not None:
                self.arrow.remove()
            self.arrow = self.ax.annotate(
                "", xy=(avg_angle, 0.5), xytext=(avg_angle, 0.1),
                arrowprops=dict(facecolor="black", arrowstyle="->", lw=2),
            )
        self.ax.set_title(self.clicked_spin[0]+" "+str(self.clicked_spin[1]), fontsize=12, y=1.15)
        self.figure.tight_layout()
        self.canvas.draw_idle()

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
            if self.canvas_visible: self.update_spins_plot()
            self.update()
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
            for key, entities in self.agents_shapes.items():
                idx = 0
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
                    if self.clicked_spin is not None and self.clicked_spin[0]==key and self.clicked_spin[1]==idx:
                        # Draw a circle that envelopes the entity_vertices
                        xs = [point.x() for point in entity_vertices]
                        ys = [point.y() for point in entity_vertices]
                        centroid_x = sum(xs) / len(xs)
                        centroid_y = sum(ys) / len(ys)
                        # Compute max distance from centroid to any vertex
                        max_radius = max(math.hypot(x - centroid_x, y - centroid_y) for x, y in zip(xs, ys))
                        # Draw the circle
                        circle = self.scene.addEllipse(
                            centroid_x - max_radius,
                            centroid_y - max_radius,
                            2 * max_radius,
                            2 * max_radius,
                            QPen(QColor("white"), 1),
                            QBrush(Qt.NoBrush)
                        )
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
                    idx += 1

