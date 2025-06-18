import math
from geometry_utils.vector3D import Vector3D

_PI = math.pi
class Shape3DFactory:
    @staticmethod
    def create_shape(_object:str, shape_type:str, config_elem:dict):
        if shape_type == "sphere":
            return Sphere(_object, shape_type, config_elem)
        elif shape_type in ("square", "cube", "rectangle", "cuboid"):
            return Cuboid(_object, shape_type, config_elem)
        elif shape_type in ("circle", "cylinder"):
            return Cylinder(_object, shape_type, config_elem)
        elif shape_type == "point" or shape_type == "none":
            return Shape(config_elem)
        else:
            raise ValueError(f"Unknown shape type: {shape_type}")

class Shape:
    dense_shapes = ["sphere", "cube", "cuboid", "cylinder"]
    flat_shapes = ["circle", "square", "rectangle"]
    no_shapes = ["point", "none"]

    def __init__(self, config_elem:dict, center: Vector3D = Vector3D()):
        self.center = Vector3D(center.x, center.y, center.z)
        self._object = "arena"
        self._id = "point"
        self._color = config_elem.get("color", "white")
        self.vertices_list = []
        self.attachments = []

    def add_attachment(self, attachment):
        self.attachments.append(attachment)

    def get_attachments(self):
        return self.attachments

    def translate_attachments(self, angle: float):
        max_v = self.max_vert()
        angle_rad = math.radians(angle)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        cx, cy = self.center.x, self.center.y
        dx = max_v.x - cx - .01
        dy = max_v.y - cy - .01
        for attachment in self.attachments:
            attachment.translate(Vector3D(
                cx + dx * cos_a,
                cy + dy * -sin_a,
                max_v.z
            ))

    def color(self) -> str:
        return self._color

    def set_color(self, color: str):
        self._color = color

    def center_of_mass(self) -> Vector3D:
        return self.center

    def vertices(self) -> list:
        return self.vertices_list

    def translate(self, new_center: Vector3D):
        self.center = new_center
        self.set_vertices()

    def get_radius(self) -> float:
        return 0

    def set_vertices(self):
        pass

    def check_overlap(self, _shape):
        # Usa direttamente self.vertices_list invece di self.vertices()
        for vertex in self.vertices_list:
            if _shape._object == "arena":
                if not self._is_point_inside_shape(vertex, _shape):
                    return True, vertex
            else:
                if self._is_point_inside_shape(vertex, _shape):
                    return True, vertex
        for vertex in _shape.vertices_list:
            if self._is_point_inside_shape(vertex, self):
                return True, vertex
        return False, Vector3D()

    def _get_random_point_inside_shape(self, random_generator, arena_shape):
        if isinstance(arena_shape, (Cylinder, Sphere)):
            angle = random_generator.uniform(0, 2 * _PI)
            r = arena_shape.radius * math.sqrt(random_generator.uniform(0, 1))
            x = arena_shape.center.x + r * math.cos(angle)
            y = arena_shape.center.y + r * math.sin(angle)
            z = arena_shape.center.z
            return Vector3D(x, y, z)
        else:
            min_v = arena_shape.min_vert()
            max_v = arena_shape.max_vert()
            if isinstance(self, (Cylinder, Sphere)):
                tmp = self.get_radius()
                min_v += Vector3D(tmp, tmp, tmp)
                max_v -= Vector3D(tmp, tmp, tmp)
            else:
                tmp = self.center - self.max_vert()
                min_v += tmp
                max_v -= tmp
            return Vector3D(
                random_generator.uniform(min_v.x, max_v.x),
                random_generator.uniform(min_v.y, max_v.y),
                random_generator.uniform(min_v.z, max_v.z)
            )

    def _is_point_inside_shape(self, point, shape):
        if isinstance(shape, Cylinder):
            dx = point.x - shape.center.x
            dy = point.y - shape.center.y
            dz = point.z - shape.center.z
            distance = math.sqrt(dx * dx + dy * dy + dz * dz)
            return distance <= shape.radius
        else:
            min_v = shape.min_vert()
            max_v = shape.max_vert()
            return (min_v.x <= point.x <= max_v.x and
                    min_v.y <= point.y <= max_v.y and
                    min_v.z <= point.z <= max_v.z)

    def rotate(self, angle_z: float):
        angle_rad_z = math.radians(angle_z)
        if angle_rad_z > 0:
            cos_z = math.cos(angle_rad_z)
            sin_z = math.sin(angle_rad_z)
            cx, cy = self.center.x, self.center.y
            for vertex in self.vertices_list:
                # Ottimizza la rotazione solo sul piano XY
                x_shift = vertex.x - cx
                y_shift = vertex.y - cy
                x_new = cx + x_shift * cos_z - y_shift * sin_z
                y_new = cy + x_shift * sin_z + y_shift * cos_z
                vertex.x, vertex.y = x_new, y_new

    def min_vert(self):
        # Usa min/max con generator expression per efficienza
        if not self.vertices_list:
            return Vector3D()
        return Vector3D(
            min(v.x for v in self.vertices_list),
            min(v.y for v in self.vertices_list),
            min(v.z for v in self.vertices_list)
        )

    def max_vert(self):
        if not self.vertices_list:
            return Vector3D()
        return Vector3D(
            max(v.x for v in self.vertices_list),
            max(v.y for v in self.vertices_list),
            max(v.z for v in self.vertices_list)
        )

class Sphere(Shape):
    def __init__(self, _object: str, shape_type: str, config_elem: dict, center: Vector3D = Vector3D()):
        super().__init__(config_elem=config_elem, center=center)
        self._object = _object
        self._id = shape_type
        self.radius = config_elem.get("diameter", 1.0) * 0.5
        self.set_vertices()

    def volume(self):
        return (4 / 3) * _PI * self.radius ** 3

    def get_radius(self) -> float:
        return self.radius

    def surface_area(self):
        return 4 * _PI * self.radius ** 2

    def set_vertices(self):
        self.vertices_list = []
        num_vertices = 32  # Ridotto per efficienza, aumenta se serve più precisione
        cx, cy, cz = self.center.x, self.center.y, self.center.z
        r = self.radius
        for i in range(num_vertices):
            theta = 2 * _PI * (i / num_vertices)
            cos_theta = math.cos(theta)
            sin_theta = math.sin(theta)
            for j in range(num_vertices):
                phi = _PI * j / num_vertices
                sin_phi = math.sin(phi)
                x = cx + r * sin_phi * cos_theta
                y = cy + r * sin_phi * sin_theta
                z = cz + r * math.cos(phi)
                self.vertices_list.append(Vector3D(x, y, z))

class Cuboid(Shape):
    def __init__(self, _object: str, shape_type: str, config_elem: dict, center: Vector3D = Vector3D()):
        super().__init__(config_elem=config_elem, center=center)
        self._object = _object
        self._id = shape_type
        self.width = config_elem.get("width", 1.0)
        self.height = config_elem.get("height", 1.0)
        self.depth = config_elem.get("depth", 1.0)
        self.set_vertices()

    def volume(self):
        if self._id in Shape.flat_shapes:
            return self.width * self.depth
        else:
            return self.width * self.height * self.depth

    def surface_area(self):
        if self._id in Shape.flat_shapes:
            return self.width * self.depth
        else:
            return 2 * (self.width * self.height + self.height * self.depth + self.depth * self.width)

    def set_vertices(self):
        half_width = self.width * 0.5
        half_height = self.height * 0.5
        half_depth = self.depth * 0.5
        cx, cy, cz = self.center.x, self.center.y, self.center.z
        if self._object == "arena":
            self.vertices_list = [
                Vector3D(cx - half_width, cy - half_depth, 0),
                Vector3D(cx - half_width, cy - half_depth, self.height),
                Vector3D(cx + half_width, cy - half_depth, 0),
                Vector3D(cx + half_width, cy - half_depth, self.height),
                Vector3D(cx + half_width, cy + half_depth, 0),
                Vector3D(cx + half_width, cy + half_depth, self.height),
                Vector3D(cx - half_width, cy + half_depth, 0),
                Vector3D(cx - half_width, cy + half_depth, self.height)
            ]
        else:
            if self._id in Shape.flat_shapes:
                self.center.z = 0
                self.vertices_list = [
                    Vector3D(cx - half_width, cy - half_depth, 0),
                    Vector3D(cx + half_width, cy - half_depth, 0),
                    Vector3D(cx + half_width, cy + half_depth, 0),
                    Vector3D(cx - half_width, cy + half_depth, 0)
                ]
            else:
                self.vertices_list = [
                    Vector3D(cx - half_width, cy - half_depth, cz - half_height),
                    Vector3D(cx - half_width, cy - half_depth, cz + half_height),
                    Vector3D(cx + half_width, cy - half_depth, cz - half_height),
                    Vector3D(cx + half_width, cy - half_depth, cz + half_height),
                    Vector3D(cx + half_width, cy + half_depth, cz - half_height),
                    Vector3D(cx + half_width, cy + half_depth, cz + half_height),
                    Vector3D(cx - half_width, cy + half_depth, cz - half_height),
                    Vector3D(cx - half_width, cy + half_depth, cz + half_height)
                ]

class Cylinder(Shape):
    def __init__(self, _object: str, shape_type: str, config_elem: dict, center: Vector3D = Vector3D()):
        super().__init__(config_elem=config_elem, center=center)
        self._object = _object
        self._id = shape_type
        self.radius = config_elem.get("diameter", 1.0) * 0.5
        self.height = config_elem.get("height", 1.0)
        self.set_vertices()

    def volume(self):
        return _PI * self.radius ** 2 * self.height

    def get_radius(self) -> float:
        return self.radius

    def surface_area(self):
        return 2 * _PI * self.radius * (self.radius + self.height)

    def set_vertices(self):
        self.vertices_list = []
        if self._object == "arena":
            num_vertices = 20
            angle_increment = 2 * _PI / num_vertices
            cx, cy = self.center.x, self.center.y
            for i in range(num_vertices):
                angle = i * angle_increment
                cos_a = math.cos(angle)
                sin_a = math.sin(angle)
                x = cx + self.radius * cos_a
                y = cy + self.radius * sin_a
                z1 = 0
                z2 = self.height
                self.vertices_list.append(Vector3D(x, y, z1))
                self.vertices_list.append(Vector3D(x, y, z2))
        else:
            num_vertices = 8 if self._object == "mark" else 16
            angle_increment = 2 * _PI / num_vertices
            cx, cy, cz = self.center.x, self.center.y, self.center.z
            if self._id in Shape.flat_shapes:
                self.center.z = 0
                for i in range(num_vertices):
                    angle = i * angle_increment
                    cos_a = math.cos(angle)
                    sin_a = math.sin(angle)
                    x = cx + self.radius * cos_a
                    y = cy + self.radius * sin_a
                    self.vertices_list.append(Vector3D(x, y, 0))
            else:
                half_height = self.height * 0.5
                for i in range(num_vertices):
                    angle = i * angle_increment
                    cos_a = math.cos(angle)
                    sin_a = math.sin(angle)
                    x = cx + self.radius * cos_a
                    y = cy + self.radius * sin_a
                    self.vertices_list.append(Vector3D(x, y, cz - half_height))
                    self.vertices_list.append(Vector3D(x, y, cz + half_height))