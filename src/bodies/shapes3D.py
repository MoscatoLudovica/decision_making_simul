import math
import numpy as np
from geometry_utils.vector3D import Vector3D

class Shape3DFactory:
    @staticmethod
    def create_shape(_object:str,shape_type:str, config_elem:dict):
        if shape_type == "sphere":
            return Sphere(_object,shape_type,config_elem)
        elif shape_type in ("square","cube"):
            return Cuboid(_object,shape_type,config_elem)
        elif shape_type in ("rectangle","cuboid"):
            return Cuboid(_object,shape_type,config_elem)
        elif shape_type in ("circle","cylinder"):
            return Cylinder(_object,shape_type,config_elem)
        elif shape_type == "point" or shape_type == "none":
            return Shape(config_elem)
        else:
            raise ValueError(f"Unknown shape type: {shape_type}")

class Shape:
    rounding = 4
    dense_shapes = ["sphere", "cube", "cuboid", "cylinder"]
    flat_shapes = ["circle","square", "rectangle"]
    no_shapes = ["point", "none"]
    def __init__(self, config_elem:dict, center: Vector3D = Vector3D()):
        self.center = Vector3D(np.round(center.x,Shape.rounding),np.round(center.y,Shape.rounding),np.round(center.z,Shape.rounding))
        self._object = "arena"
        self._id = "point"
        self._color = config_elem.get("color", "white")
        self.vertices_list = []

    def color(self) -> str:
        return self._color
    
    def center_of_mass(self) -> Vector3D:
        return self.center

    def vertices(self) -> list:
        return self.vertices_list
    
    def translate(self, translation_vector:Vector3D):
        self.center = self.center + translation_vector
        self.set_vertices()
    
    def set_vertices(self):
        pass

    def check_overlap(self, _shape):
        for vertex in self.vertices():
            if _shape._object == "arena":
                if self._is_point_outside_shape(vertex, _shape):
                    return True, vertex
            else:
                if self._is_point_inside_shape(vertex, _shape):
                    return True, vertex
        for vertex in _shape.vertices():
            if self._is_point_inside_shape(vertex, self):
                return True, vertex
        return False, Vector3D()

    def _is_point_inside_shape(self, point, shape):
        # This is a placeholder method. The actual implementation will depend on the specific shape.
        # For simplicity, let's assume it checks if a point is inside a bounding box of the shape.
        min_v = shape.min_vert()
        max_v = shape.max_vert()

        return (min_v.x <= point.x <= max_v.x and
                min_v.y <= point.y <= max_v.y and
                min_v.z <= point.z <= max_v.z)
    
    def _is_point_outside_shape(self, point, shape):
        # This is a placeholder method. The actual implementation will depend on the specific shape.
        # For simplicity, let's assume it checks if a point is inside a bounding box of the shape.
        min_v = shape.min_vert()
        max_v = shape.max_vert()

        return (not (min_v.x <= point.x <= max_v.x) or
                not (min_v.y <= point.y <= max_v.y) or
                not (min_v.z <= point.z <= max_v.z))

    def rotate_x(self, angle:float):
        angle_rad = math.radians(angle)
        for vertex in self.vertices():
            rotated_vertex = vertex.v_rotate_x(self.center, angle_rad)
            new_vertex = rotated_vertex + self.center
            vertex.x, vertex.y, vertex.z = new_vertex.x, new_vertex.y, new_vertex.z

    def rotate_y(self, angle:float):
        angle_rad = math.radians(angle)
        for vertex in self.vertices():
            rotated_vertex = vertex.v_rotate_y(self.center, angle_rad)
            new_vertex = rotated_vertex + self.center
            vertex.x, vertex.y, vertex.z = new_vertex.x, new_vertex.y, new_vertex.z

    def rotate_z(self, angle:float):
        angle_rad = math.radians(angle)
        for vertex in self.vertices():
            rotated_vertex = vertex.v_rotate_z(self.center, angle_rad)
            new_vertex = rotated_vertex + self.center
            vertex.x, vertex.y, vertex.z = new_vertex.x, new_vertex.y, new_vertex.z

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

    def surface_area(self):
        return 4 * math.pi * self.radius ** 2

    def set_vertices(self):
        self.vertices_list = []
        num_vertices = 90
        for i in range(num_vertices):
            theta = 2 * math.pi * (i / num_vertices)
            for j in range(num_vertices):
                phi = math.pi * j / num_vertices
                x = self.center.x + self.radius * math.sin(phi) * math.cos(theta)
                y = self.center.y + self.radius * math.sin(phi) * math.sin(theta)
                z = self.center.z + self.radius * math.cos(phi)
                self.vertices_list.append(Vector3D(np.round(x,Shape.rounding), np.round(y,Shape.rounding), np.round(z,Shape.rounding)))
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
                Vector3D(np.round(cx - half_width,Shape.rounding), np.round(cy - half_depth,Shape.rounding), 0),
                Vector3D(np.round(cx + half_width,Shape.rounding), np.round(cy - half_depth,Shape.rounding), 0),
                Vector3D(np.round(cx + half_width,Shape.rounding), np.round(cy + half_depth,Shape.rounding), 0),
                Vector3D(np.round(cx - half_width,Shape.rounding), np.round(cy + half_depth,Shape.rounding), 0),
                Vector3D(np.round(cx - half_width,Shape.rounding), np.round(cy - half_depth,Shape.rounding), np.round(self.height,Shape.rounding)),
                Vector3D(np.round(cx + half_width,Shape.rounding), np.round(cy - half_depth,Shape.rounding), np.round(self.height,Shape.rounding)),
                Vector3D(np.round(cx + half_width,Shape.rounding), np.round(cy + half_depth,Shape.rounding), np.round(self.height,Shape.rounding)),
                Vector3D(np.round(cx - half_width,Shape.rounding), np.round(cy + half_depth,Shape.rounding), np.round(self.height,Shape.rounding))
            ]
        else:
            if self._id in Shape.flat_shapes:
                self.center.z = 0
                self.vertices_list = [
                    Vector3D(np.round(cx - half_width,Shape.rounding), np.round(cy - half_depth,Shape.rounding), 0),
                    Vector3D(np.round(cx + half_width,Shape.rounding), np.round(cy - half_depth,Shape.rounding), 0),
                    Vector3D(np.round(cx + half_width,Shape.rounding), np.round(cy + half_depth,Shape.rounding), 0),
                    Vector3D(np.round(cx - half_width,Shape.rounding), np.round(cy + half_depth,Shape.rounding), 0)
                ]
            else:
                self.vertices_list = [
                    Vector3D(np.round(cx - half_width,Shape.rounding), np.round(cy - half_depth,Shape.rounding), np.round(cz - half_height,Shape.rounding)),
                    Vector3D(np.round(cx + half_width,Shape.rounding), np.round(cy - half_depth,Shape.rounding), np.round(cz - half_height,Shape.rounding)),
                    Vector3D(np.round(cx + half_width,Shape.rounding), np.round(cy + half_depth,Shape.rounding), np.round(cz - half_height,Shape.rounding)),
                    Vector3D(np.round(cx - half_width,Shape.rounding), np.round(cy + half_depth,Shape.rounding), np.round(cz - half_height,Shape.rounding)),
                    Vector3D(np.round(cx - half_width,Shape.rounding), np.round(cy - half_depth,Shape.rounding), np.round(cz + half_height,Shape.rounding)),
                    Vector3D(np.round(cx + half_width,Shape.rounding), np.round(cy - half_depth,Shape.rounding), np.round(cz + half_height,Shape.rounding)),
                    Vector3D(np.round(cx + half_width,Shape.rounding), np.round(cy + half_depth,Shape.rounding), np.round(cz + half_height,Shape.rounding)),
                    Vector3D(np.round(cx - half_width,Shape.rounding), np.round(cy + half_depth,Shape.rounding), np.round(cz + half_height,Shape.rounding))
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

    def surface_area(self):
        return 2 * math.pi * self.radius * (self.radius + self.height)

    def set_vertices(self):
        self.vertices_list = []
        num_vertices = 90
        angle_increment = 2 * math.pi / num_vertices
        if self._object == "arena":
            for i in range(num_vertices):
                angle = i * angle_increment
                x = self.center.x + self.radius * math.cos(angle)
                y = self.center.y + self.radius * math.sin(angle)
                z1 = 0
                z2 = self.height
                self.vertices_list.append(Vector3D(np.round(x,Shape.rounding), np.round(y,Shape.rounding), np.round(z1,Shape.rounding)))
                self.vertices_list.append(Vector3D(np.round(x,Shape.rounding), np.round(y,Shape.rounding), np.round(z2,Shape.rounding)))
        else:
            for i in range(num_vertices):
                angle = i * angle_increment
                x = self.center.x + self.radius * math.cos(angle)
                y = self.center.y + self.radius * math.sin(angle)
                z = 0
                if self._id in Shape.flat_shapes:
                    self.center.z = z
                    self.vertices_list.append(Vector3D(np.round(x,Shape.rounding), np.round(y,Shape.rounding), np.round(z,Shape.rounding)))
                else:
                    z1 = self.center.z - self.height * 0.5
                    z2 = self.center.z + self.height * 0.5
                    self.vertices_list.append(Vector3D(np.round(x,Shape.rounding), np.round(y,Shape.rounding), np.round(z1,Shape.rounding)))
                    self.vertices_list.append(Vector3D(np.round(x,Shape.rounding), np.round(y,Shape.rounding), np.round(z2,Shape.rounding)))