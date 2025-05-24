import math
from geometry_utils.vector3D import Vector3D

class Shape3DFactory:
    @staticmethod
    def create_shape(_object:str,shape_type:str, config_elem:dict):
        if shape_type == "sphere":
            return Sphere(_object,shape_type,config_elem)
        elif shape_type in ("square","cube","rectangle","cuboid"):
            return Cuboid(_object,shape_type,config_elem)
        elif shape_type in ("circle","cylinder"):
            return Cylinder(_object,shape_type,config_elem)
        elif shape_type == "point" or shape_type == "none":
            return Shape(config_elem)
        else:
            raise ValueError(f"Unknown shape type: {shape_type}")

class Shape:
    dense_shapes = ["sphere", "cube", "cuboid", "cylinder"]
    flat_shapes = ["circle","square", "rectangle"]
    no_shapes = ["point", "none"]
    def __init__(self, config_elem:dict, center: Vector3D = Vector3D()):
        self.center = Vector3D(center.x,center.y,center.z)
        self._object = "arena"
        self._id = "point"
        self._color = config_elem.get("color", "white")
        self.vertices_list = []
        self.attachments = []
        
    def add_attachment(self, attachment):
        self.attachments.append(attachment)
        
    def get_attachments(self):
        return self.attachments

    def translate_attachments(self,angle:float):
        max_v = self.max_vert()
        angle_rad = math.radians(angle)
        for attachment in self.attachments:
            attachment.translate(Vector3D(self.center.x + (((max_v.x - self.center.x) - .01) * math.cos(angle_rad)),
                                          self.center.y + (((max_v.y - self.center.y) - .01) * -math.sin(angle_rad)),
                                          max_v.z))

    def color(self) -> str:
        return self._color
    
    def set_color(self,color:str):
        self._color = color
    
    def center_of_mass(self) -> Vector3D:
        return self.center

    def vertices(self) -> list:
        return self.vertices_list
    
    def translate(self, new_center:Vector3D):
        self.center = new_center
        self.set_vertices()

    def get_radius(self) -> float:
        return 0

    def set_vertices(self):
        pass

    def check_overlap(self, _shape):
        for vertex in self.vertices():
            if _shape._object == "arena":
                if not self._is_point_inside_shape(vertex, _shape):
                    return True, vertex
            else:
                if self._is_point_inside_shape(vertex, _shape):
                    return True, vertex
        for vertex in _shape.vertices():
            if self._is_point_inside_shape(vertex, self):
                return True, vertex
        return False, Vector3D()

    def _get_random_point_inside_shape(self, random_generator, arena_shape):
        if isinstance(arena_shape, (Cylinder,Sphere)):
            # Generate a random point inside the circle (base of the cylinder)
            angle = random_generator.uniform(0, 2 * math.pi)
            r = arena_shape.radius * math.sqrt(random_generator.uniform(0, 1)) 
            x = arena_shape.center.x + r * math.cos(angle)
            y = arena_shape.center.y + r * math.sin(angle)
            z = arena_shape.center.z
            return Vector3D(x, y, z)
        else:
            min_v = arena_shape.min_vert()
            max_v = arena_shape.max_vert()
            if isinstance(self, (Cylinder,Sphere)):
                tmp = self.get_radius()
                min_v += Vector3D(tmp, tmp, tmp)
                max_v -= Vector3D(tmp, tmp, tmp)
            else:
                tmp = self.center - self.max_vert() 
                min_v += tmp
                max_v -= tmp
            return Vector3D(random_generator.uniform(min_v.x, max_v.x),
                            random_generator.uniform(min_v.y, max_v.y),
                            random_generator.uniform(min_v.z, max_v.z))
    
    def _is_point_inside_shape(self, point, shape):
        # This is a placeholder method. The actual implementation will depend on the specific shape.
        # For simplicity, let's assume it checks if a point is inside a bounding box of the shape.
        if isinstance(shape, Cylinder):
            distance = math.sqrt((point.x - shape.center.x) ** 2 +
                                (point.y - shape.center.y) ** 2 +
                                (point.z - shape.center.z) ** 2)
            return distance <= shape.radius
        else:
            min_v = shape.min_vert()
            max_v = shape.max_vert()

            return (min_v.x <= point.x <= max_v.x and
                    min_v.y <= point.y <= max_v.y and
                    min_v.z <= point.z <= max_v.z)
        
    def rotate(self,angle_z:float):
        angle_rad_z = math.radians(angle_z)
        if angle_rad_z>0:
            for vertex in self.vertices():
                rotated_vertex = vertex.v_rotate_z(self.center, angle_rad_z)
                vertex.x, vertex.y, vertex.z = rotated_vertex.x, rotated_vertex.y, rotated_vertex.z

    def min_vert(self):
        out_x,out_y,out_z = 99999,99999,99999
        for v in self.vertices_list:
            if v.x < out_x: out_x = v.x
            if v.y < out_y: out_y = v.y
            if v.z < out_z: out_z = v.z
        return Vector3D(out_x,out_y,out_z)

    def max_vert(self):
        out_x,out_y,out_z = -1,-1,-1
        for v in self.vertices_list:
            if v.x > out_x: out_x = v.x
            if v.y > out_y: out_y = v.y
            if v.z > out_z: out_z = v.z
        return Vector3D(out_x,out_y,out_z)
        
class Sphere(Shape):
    def __init__(self,_object:str,shape_type:str, config_elem:dict, center: Vector3D = Vector3D()):
        super().__init__(config_elem=config_elem, center=center)
        self._object = _object
        self._id = shape_type
        self.radius = config_elem.get("diameter", 1.0) * 0.5

    def volume(self):
        return (4/3) * math.pi * self.radius ** 3

    def get_radius(self) -> float:
        return self.radius

    def surface_area(self):
        return 4 * math.pi * self.radius ** 2

    def set_vertices(self):
        self.vertices_list = []
        num_vertices = 64
        for i in range(num_vertices):
            theta = 2 * math.pi * (i / num_vertices)
            for j in range(num_vertices):
                phi = math.pi * j / num_vertices
                x = self.center.x + self.radius * math.sin(phi) * math.cos(theta)
                y = self.center.y + self.radius * math.sin(phi) * math.sin(theta)
                z = self.center.z + self.radius * math.cos(phi)
                self.vertices_list.append(Vector3D(x, y, z))

class Cuboid(Shape):
    def __init__(self,_object:str,shape_type:str, config_elem:dict, center: Vector3D = Vector3D()):
        super().__init__(config_elem=config_elem, center=center)
        self._object = _object
        self._id = shape_type
        self.width = config_elem.get("width", 1.0)
        self.height = config_elem.get("height", 1.0)
        self.depth = config_elem.get("depth", 1.0)
        self.set_vertices()

    def volume(self):
        if self._id in Shape.flat_shapes: return self.width * self.depth
        else: return self.width * self.height * self.depth

    def surface_area(self):
        if self._id in Shape.flat_shapes: return self.width * self.depth
        else: return 2 * (self.width * self.height + self.height * self.depth + self.depth * self.width)

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
    def __init__(self,_object:str,shape_type:str, config_elem:dict, center: Vector3D = Vector3D()):
        super().__init__(config_elem=config_elem, center=center)
        self._object = _object
        self._id = shape_type
        self.radius = config_elem.get("diameter", 1.0) * 0.5
        self.height = config_elem.get("height", 1.0)
        self.set_vertices()

    def volume(self):
        return math.pi * self.radius ** 2 * self.height

    def get_radius(self) -> float:
        return self.radius
    
    def surface_area(self):
        return 2 * math.pi * self.radius * (self.radius + self.height)

    def set_vertices(self):
        self.vertices_list = []
        num_vertices = 20
        angle_increment = 2 * math.pi / num_vertices
        if self._object == "arena":
            for i in range(num_vertices):
                angle = i * angle_increment
                x = self.center.x + self.radius * math.cos(angle)
                y = self.center.y + self.radius * math.sin(angle)
                z1 = 0
                z2 = self.height
                self.vertices_list.append(Vector3D(x, y, z1))
                self.vertices_list.append(Vector3D(x, y, z2))
        else:
            num_vertices = 8 if self._object == "mark" else 16
            angle_increment = 2 * math.pi / num_vertices
            for i in range(num_vertices):
                angle = i * angle_increment
                x = self.center.x + self.radius * math.cos(angle)
                y = self.center.y + self.radius * math.sin(angle)
                z = 0
                if self._id in Shape.flat_shapes:
                    self.center.z = z
                    self.vertices_list.append(Vector3D(x, y, z))
                else:
                    z1 = self.center.z - self.height * 0.5
                    z2 = self.center.z + self.height * 0.5
                    self.vertices_list.append(Vector3D(x, y, z1))
                    self.vertices_list.append(Vector3D(x, y, z2))