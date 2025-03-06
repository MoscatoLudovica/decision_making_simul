import math
from geometry_utils.vector3D import Vector3D

class Shape3DFactory:
    @staticmethod
    def create_shape(shape_type:str,config_elem:dict):
        if shape_type == "sphere":
            return Sphere(config_elem)
        elif shape_type == "cube":
            return Cube(config_elem)
        elif shape_type == "cuboid":
            return Cuboid(config_elem)
        elif shape_type == "pyramid":
            return Pyramid(config_elem)
        elif shape_type == "cone":
            return Cone(config_elem)
        elif shape_type == "cylinder":
            return Cylinder(config_elem)
        elif shape_type == "point" or shape_type == "none":
            return Shape(config_elem)
        else:
            raise ValueError(f"Unknown shape type: {shape_type}")
        
class Shape:

    def __init__(self,config_elem:dict,center: Vector3D = Vector3D()):
        self.center = center
        if config_elem != None:
            self.height = config_elem.get("height", 0.01)
            self.color = config_elem.get("color", "white")

    def configure(self):
        pass

    def volume(self) -> float:
        pass

    def surface_area(self) -> float:
        pass

    def center_of_mass(self) -> Vector3D:
        pass

    def vertices(self) -> list:
        pass

    def translate(self, translation_vector):
        self.center = self.center + translation_vector
        self.set_vertices()

    def scale(self, scale_factor):
        pass

    def set_vertices(self):
        pass

    def rotate_x(self, angle:float):
        for vertex in self.vertices():
            rotated_vertex = vertex.v_rotate_x(self.center,angle)
            new_vertex = rotated_vertex + self.center
            vertex.x, vertex.y, vertex.z = new_vertex.x, new_vertex.y, new_vertex.z

    def rotate_y(self, angle:float):
        for vertex in self.vertices():
            rotated_vertex = vertex.v_rotate_y(self.center,angle)
            new_vertex = rotated_vertex + self.center
            vertex.x, vertex.y, vertex.z = new_vertex.x, new_vertex.y, new_vertex.z

    def rotate_z(self, angle:float):
        for vertex in self.vertices():
            rotated_vertex = vertex.v_rotate_z(self.center,angle)
            new_vertex = rotated_vertex + self.center
            vertex.x, vertex.y, vertex.z = new_vertex.x, new_vertex.y, new_vertex.z

class Sphere(Shape):

    def __init__(self, radius:float, config_elem:dict):
        super().__init__(config_elem=config_elem)
        self.radius = radius
        self.vertices_list = []

    def configure(self, radius:float, new_center:Vector3D):
        super().__init__(config_elem=None,center=new_center)
        self.radius = radius

    def volume(self):
        return (4/3) * math.pi * self.radius ** 3

    def surface_area(self):
        return 4 * math.pi * self.radius ** 2

    def center_of_mass(self):
        return self.center

    def vertices(self):
        return self.vertices_list

    def set_vertices(self):
        self.vertices_list = []

class Cube(Shape):

    def __init__(self, side_length:float, config_elem:dict):
        super().__init__(config_elem=config_elem)
        self.side_length = side_length
        self.set_vertices()

    def configure(self, side_length:float, new_center:Vector3D):
        super().__init__(config_elem=None,center=new_center)
        self.side_length = side_length
        self.set_vertices()

    def volume(self):
        return self.side_length ** 3

    def surface_area(self):
        return 6 * self.side_length ** 2

    def center_of_mass(self):
        return self.center

    def vertices(self):
        return self.vertices_list

    def set_vertices(self):
        half_side = self.side_length * .5
        cx, cy, cz = self.center.x, self.center.y, self.center.z
        self.vertices_list = [
            Vector3D(cx - half_side, cy - half_side, cz - half_side),
            Vector3D(cx + half_side, cy - half_side, cz - half_side),
            Vector3D(cx + half_side, cy + half_side, cz - half_side),
            Vector3D(cx - half_side, cy + half_side, cz - half_side),
            Vector3D(cx - half_side, cy - half_side, cz + half_side),
            Vector3D(cx + half_side, cy - half_side, cz + half_side),
            Vector3D(cx + half_side, cy + half_side, cz + half_side),
            Vector3D(cx - half_side, cy + half_side, cz + half_side)
        ]

class Cuboid(Shape):
    def __init__(self, width:float, height:float, depth:float, config_elem):
        super().__init__(config_elem)
        self.width = width
        self.height = height
        self.depth = depth
        self.set_vertices()

    def configure(self, width:float, height:float, depth:float, new_center:Vector3D):
        super().__init__(config_elem=None,center=new_center)
        self.width = width
        self.height = height
        self.depth = depth
        self.set_vertices()

    def volume(self):
        return self.width * self.height * self.depth

    def surface_area(self):
        return 2 * (self.width * self.height + self.height * self.depth + self.depth * self.width)

    def center_of_mass(self):
        return self.center

    def vertices(self):
        return self.vertices_list

    def set_vertices(self):
        half_width = self.width * .5
        half_height = self.height * .5
        half_depth = self.depth * .5
        cx, cy, cz = self.center.x, self.center.y, self.center.z
        self.vertices_list = [
            Vector3D(cx - half_width, cy - half_height, cz - half_depth),
            Vector3D(cx + half_width, cy - half_height, cz - half_depth),
            Vector3D(cx + half_width, cy + half_height, cz - half_depth),
            Vector3D(cx - half_width, cy + half_height, cz - half_depth),
            Vector3D(cx - half_width, cy - half_height, cz + half_depth),
            Vector3D(cx + half_width, cy - half_height, cz + half_depth),
            Vector3D(cx + half_width, cy + half_height, cz + half_depth),
            Vector3D(cx - half_width, cy + half_height, cz + half_depth)
        ]

class Pyramid(Shape):
    def __init__(self, base_length:float, base_width:float, height:float, config_elem:dict):
        super().__init__(config_elem)
        self.base_length = base_length
        self.base_width = base_width
        self.height = height
        self.set_vertices()

    def configure(self, base_length:float, base_width:float, height:float, new_center:Vector3D):            
        super().__init__(config_elem=None, center=new_center)
        self.base_length = base_length
        self.base_width = base_width
        self.height = height
        self.set_vertices()

    def volume(self):
        return (1/3) * self.base_length * self.base_width * self.height

    def surface_area(self):
        base_area = self.base_length * self.base_width
        slant_height1 = math.sqrt((self.base_length * .5) ** 2 + self.height ** 2)
        slant_height2 = math.sqrt((self.base_width * .5) ** 2 + self.height ** 2)
        lateral_area = self.base_length * slant_height1 + self.base_width * slant_height2
        return base_area + lateral_area

    def center_of_mass(self):
        return Vector3D(self.center.x, self.center.y, self.center.z + self.height * .25)

    def vertices(self):
        return self.vertices_list

    def set_vertices(self):
        half_length = self.base_length * .5
        half_width = self.base_width * .5
        cx, cy, cz = self.center.x, self.center.y, self.center.z
        self.vertices_list = [
            Vector3D(cx - half_length, cy - half_width, cz),
            Vector3D(cx + half_length, cy - half_width, cz),
            Vector3D(cx + half_length, cy + half_width, cz),
            Vector3D(cx - half_length, cy + half_width, cz),
            Vector3D(cx, cy, cz + self.height)
        ]

class Cone(Shape):
    def __init__(self, radius:float, height:float, config_elem:dict):
        super().__init__(config_elem)
        self.radius = radius
        self.height = height
        self.vertices_list = []

    def configure(self, radius:float, height:float, new_center:Vector3D):
        super().__init__(config_elem=None,center=new_center)
        self.radius = radius
        self.height = height

    def volume(self):
        return (1/3) * math.pi * self.radius ** 3

    def surface_area(self):
        slant_height = math.sqrt(self.radius ** 2 + self.height ** 2)
        return math.pi * self.radius * (self.radius + slant_height)

    def center_of_mass(self):
        return Vector3D(self.center.x, self.center.y, self.center.z + self.height * .25)

    def vertices(self):
        return self.vertices_list

    def set_vertices(self):
        self.vertices_list = []

class Cylinder(Shape):
    def __init__(self, radius:float, height:float, config_elem):
        super().__init__(config_elem)
        self.radius = radius
        self.height = height
        self.vertices_list = []
    
    def configure(self, radius:float, height:float, new_center:Vector3D):
        super().__init__(config_elem=None,center=new_center)
        self.radius = radius
        self.height = height

    def volume(self):
        return math.pi * self.radius ** 2 * self.height

    def surface_area(self):
        return 2 * math.pi * self.radius * (self.radius + self.height)

    def center_of_mass(self):
        return Vector3D(self.center.x, self.center.y, self.center.z + self.height * .5)

    def vertices(self):
        return self.vertices_list

    def set_vertices(self):
        self.vertices_list = []