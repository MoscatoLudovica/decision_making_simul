import math
import numpy as np
from geometry_utils.vector3D import Vector3D

class Shape3DFactory:
    @staticmethod
    def create_shape(_object:str,shape_type:str, config_elem:dict):
        if shape_type == "sphere":
            return Sphere(_object,config_elem)
        elif shape_type in ("square","cube"):
            return Cube(_object,config_elem)
        elif shape_type in ("rectangle","cuboid"):
            return Cuboid(_object,config_elem)
        elif shape_type in ("circle","cylinder"):
            return Cylinder(_object,config_elem)
        elif shape_type == "point" or shape_type == "none":
            return Shape(_object,config_elem)
        else:
            raise ValueError(f"Unknown shape type: {shape_type}")

class Shape:
    def __init__(self, config_elem:dict, center: Vector3D = Vector3D()):
        self.center = Vector3D(np.round(center.x,3),np.round(center.y,3),np.round(center.z,3))
        self.floor = 0.0   # special entry used only for arena
        self._object = "arena"
        self.color = config_elem.get("color", "white")
        self.vertices_list = []

    def volume(self) -> float:
        pass

    def surface_area(self) -> float:
        pass

    def center_of_mass(self) -> Vector3D:
        pass

    def vertices(self) -> list:
        pass

    def translate(self, translation_vector):
        pass

    def scale(self, scale_factor):
        pass

    def set_vertices(self):
        pass

    def check_overlap(self, _shape):
        for vertex in self.vertices():
            if _shape._object == "arena":
                if self._is_point_outside_shape(vertex, _shape):
                    return True
            else:
                if self._is_point_inside_shape(vertex, _shape):
                    return True
        for vertex in _shape.vertices():
            if self._is_point_inside_shape(vertex, self):
                return True
        return False

    def _is_point_inside_shape(self, point, shape):
        # This is a placeholder method. The actual implementation will depend on the specific shape.
        # For simplicity, let's assume it checks if a point is inside a bounding box of the shape.
        min_x = min(vertex.x for vertex in shape.vertices())
        max_x = max(vertex.x for vertex in shape.vertices())
        min_y = min(vertex.y for vertex in shape.vertices())
        max_y = max(vertex.y for vertex in shape.vertices())
        min_z = min(vertex.z for vertex in shape.vertices())
        max_z = max(vertex.z for vertex in shape.vertices())

        return (min_x <= point.x <= max_x and
                min_y <= point.y <= max_y and
                min_z <= point.z <= max_z)
    
    def _is_point_outside_shape(self, point, shape):
        # This is a placeholder method. The actual implementation will depend on the specific shape.
        # For simplicity, let's assume it checks if a point is inside a bounding box of the shape.
        min_x = min(vertex.x for vertex in shape.vertices())
        max_x = max(vertex.x for vertex in shape.vertices())
        min_y = min(vertex.y for vertex in shape.vertices())
        max_y = max(vertex.y for vertex in shape.vertices())
        min_z = min(vertex.z for vertex in shape.vertices())
        max_z = max(vertex.z for vertex in shape.vertices())

        return (not (min_x <= point.x <= max_x) or
                not (min_y <= point.y <= max_y) or
                not (min_z <= point.z <= max_z))

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

    def min_vert_x(self):
        out = 99999
        for v in self.vertices_list:
            if v.x < out: out = v.x
        return out

    def max_vert_x(self):
        out = -1
        for v in self.vertices_list:
            if v.x > out: out = v.x
        return out
    
    def min_vert_y(self):
        out = 99999
        for v in self.vertices_list:
            if v.y < out: out = v.y
        return out

    def max_vert_y(self):
        out = -1
        for v in self.vertices_list:
            if v.y > out: out = v.y
        return out
    
    def min_vert_z(self):
        out = 99999
        for v in self.vertices_list:
            if v.z < out: out = v.z
        return out

    def max_vert_z(self):
        out = -1
        for v in self.vertices_list:
            if v.z > out: out = v.z
        return out

class Sphere(Shape):
    def __init__(self,_object, config_elem:dict, center: Vector3D = Vector3D()):
        super().__init__(config_elem=config_elem, center=center)
        self._object = _object
        self.radius = config_elem.get("radius", 1.0)

    def volume(self):
        return (4/3) * math.pi * self.radius ** 3

    def surface_area(self):
        return 4 * math.pi * self.radius ** 2

    def center_of_mass(self):
        return self.center

    def vertices(self):
        return self.vertices_list
    
    def translate(self, translation_vector):
        self.center = self.center + translation_vector
        self.set_vertices()

    def set_vertices(self):
        self.vertices_list = []
        num_vertices = 260
        for i in range(num_vertices):
            theta = 2 * math.pi * (i / num_vertices)
            for j in range(num_vertices):
                phi = math.pi * j / num_vertices
                x = self.center.x + self.radius * math.sin(phi) * math.cos(theta)
                y = self.center.y + self.radius * math.sin(phi) * math.sin(theta)
                z = self.center.z + self.radius * math.cos(phi)
                self.vertices_list.append(Vector3D(np.round(x,3), np.round(y,3), np.round(z,3)))

class Cube(Shape):
    def __init__(self,_object, config_elem:dict, center: Vector3D = Vector3D()):
        super().__init__(config_elem=config_elem, center=center)
        self._object = _object
        self.side_length = config_elem.get("side", 1.0)
        self.set_vertices()

    def volume(self):
        return self.side_length ** 3

    def surface_area(self):
        return 6 * self.side_length ** 2

    def center_of_mass(self):
        return self.center

    def vertices(self):
        return self.vertices_list

    def translate(self, translation_vector):
        self.center = self.center + translation_vector
        self.set_vertices()

    def set_vertices(self):
        half_side = self.side_length * 0.5
        cx, cy, cz = self.center.x, self.center.y, self.center.z
        self.vertices_list = [
            Vector3D(np.round(cx - half_side,3), np.round(cy - half_side,3), np.round(cz - half_side,3)),
            Vector3D(np.round(cx + half_side,3), np.round(cy - half_side,3), np.round(cz - half_side,3)),
            Vector3D(np.round(cx + half_side,3), np.round(cy + half_side,3), np.round(cz - half_side,3)),
            Vector3D(np.round(cx - half_side,3), np.round(cy + half_side,3), np.round(cz - half_side,3)),
            Vector3D(np.round(cx - half_side,3), np.round(cy - half_side,3), np.round(cz + half_side,3)),
            Vector3D(np.round(cx + half_side,3), np.round(cy - half_side,3), np.round(cz + half_side,3)),
            Vector3D(np.round(cx + half_side,3), np.round(cy + half_side,3), np.round(cz + half_side,3)),
            Vector3D(np.round(cx - half_side,3), np.round(cy + half_side,3), np.round(cz + half_side,3))
        ]
        if self._object == "arena":
            self.floor = self.min_vert_z()
        else:
            
        print(self._object,self.vertices_list)
        print(self.center,self.min_vert_z())

class Cuboid(Shape):
    def __init__(self,_object, config_elem:dict, center: Vector3D = Vector3D()):
        super().__init__(config_elem=config_elem, center=center)
        self._object = _object
        self.width = config_elem.get("width", 1.0)
        self.height = config_elem.get("height", 1.0)
        self.depth = config_elem.get("depth", 1.0)
        self.set_vertices()

    def volume(self):
        return self.width * self.height * self.depth

    def surface_area(self):
        return 2 * (self.width * self.height + self.height * self.depth + self.depth * self.width)

    def center_of_mass(self):
        return self.center

    def vertices(self):
        return self.vertices_list

    def translate(self, translation_vector):
        self.center = self.center + translation_vector
        self.set_vertices()

    def set_vertices(self):
        half_width = self.width * 0.5
        half_height = self.height * 0.5
        half_depth = self.depth * 0.5
        cx, cy, cz = self.center.x, self.center.y, self.center.z
        self.vertices_list = [
            Vector3D(np.round(cx - half_width,3), np.round(cy - half_depth,3), np.round(cz - half_height,3)),
            Vector3D(np.round(cx + half_width,3), np.round(cy - half_depth,3), np.round(cz - half_height,3)),
            Vector3D(np.round(cx + half_width,3), np.round(cy + half_depth,3), np.round(cz - half_height,3)),
            Vector3D(np.round(cx - half_width,3), np.round(cy + half_depth,3), np.round(cz - half_height,3)),
            Vector3D(np.round(cx - half_width,3), np.round(cy - half_depth,3), np.round(cz + half_height,3)),
            Vector3D(np.round(cx + half_width,3), np.round(cy - half_depth,3), np.round(cz + half_height,3)),
            Vector3D(np.round(cx + half_width,3), np.round(cy + half_depth,3), np.round(cz + half_height,3)),
            Vector3D(np.round(cx - half_width,3), np.round(cy + half_depth,3), np.round(cz + half_height,3))
        ]
        if self._object == "arena":
            self.floor = self.min_vert_z()

class Cylinder(Shape):
    def __init__(self,_object:str, config_elem:dict, center: Vector3D = Vector3D()):
        super().__init__(config_elem=config_elem, center=center)
        self._object = _object
        self.radius = config_elem.get("radius", 1.0)
        self.height = config_elem.get("height", 1.0)
        self.set_vertices()

    def volume(self):
        return math.pi * self.radius ** 2 * self.height

    def surface_area(self):
        return 2 * math.pi * self.radius * (self.radius + self.height)

    def center_of_mass(self):
        return Vector3D(self.center.x, self.center.y, self.center.z + self.height * 0.5)

    def vertices(self):
        return self.vertices_list

    def translate(self, translation_vector):
        self.center = self.center + translation_vector
        self.set_vertices()

    def set_vertices(self):
        self.vertices_list = []
        num_vertices = 120
        angle_increment = 2 * math.pi / num_vertices
        for i in range(num_vertices):
            angle = i * angle_increment
            x = self.center.x + self.radius * math.cos(angle)
            y = self.center.y + self.radius * math.sin(angle)
            z1 = self.center.z - self.height * 0.5
            z2 = self.center.z + self.height * 0.5
            self.vertices_list.append(Vector3D(np.round(x,3), np.round(y,3), np.round(z1,3)))
            self.vertices_list.append(Vector3D(np.round(x,3), np.round(y,3), np.round(z2,3)))
        if self._object == "arena":
            self.floor = self.min_vert_z()
        print(self._object,len(self.vertices_list))
        print(self.center,self.min_vert_z())