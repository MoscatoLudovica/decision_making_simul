import math
from geometry_utils.vector2D import Vector2D

class Shape2DFactory:
    @staticmethod
    def create_shape(shape_type:str,config_elem:dict):
        if shape_type == "circle":
            return Circle(config_elem)
        elif shape_type == "square":
            return Square(config_elem)
        elif shape_type == "rectangle":
            return Rectangle(config_elem)
        elif shape_type == "triangle":
            return Triangle(config_elem)
        elif shape_type == "point" or shape_type == "none":
            return Shape(config_elem)
        else:
            raise ValueError(f"Unknown shape type: {shape_type}")
        
class Shape:
    def __init__(self,config_elem:dict,center: Vector2D = Vector2D()):
        self.center = center
        self.height = 1   # special entry used only for arena
        self.floor = 0.05 # special entry used only for arena
        self.color = config_elem.get("color", "white")

    def configure(self):
        pass

    def area(self) -> float:
        pass

    def perimeter(self) -> float:
        pass

    def vertices(self)  -> list:
        pass

    def set_center(self, new_center: Vector2D):
        self.center = new_center

    def rotate(self, angle: float):
        pass

class Circle(Shape):
    def __init__(self, config_elem:dict):
        super().__init__(config_elem=config_elem)
        self.radius = config_elem.get("radius", 1.0)
        self._vertices = []

    def configure(self,radius:float, center: Vector2D):
        super().__init__(center)
        self.radius = radius

    def area(self):
        return math.pi * self.radius ** 2

    def perimeter(self):
        return 2 * math.pi * self.radius

    def vertices(self):
        return self._vertices

    def set_center(self, new_center: Vector2D):
        super().set_center(new_center)
        self.set_vertices()

    def set_vertices(self):
        self._vertices = []

    def rotate(self, angle: float):
        pass  # Circle rotation does not change its vertices

class Square(Shape):

    def __init__(self, config_elem:dict):
        super().__init__(config_elem=config_elem)
        self.side = config_elem.get("side", 1.0)
        self.set_vertices()
    
    def configure(self, side:float, new_center: Vector2D):
        super().__init__(new_center)
        self.side = side
        self.set_vertices()

    def area(self):
        return self.side ** 2

    def perimeter(self):
        return 4 * self.side

    def vertices(self):
        return self._vertices

    def set_center(self, new_center: Vector2D):
        super().set_center(new_center)
        self.set_vertices()

    def set_vertices(self):
        half_side = self.side * 0.5
        self._vertices = [
            Vector2D(self.center.x - half_side, self.center.y - half_side),
            Vector2D(self.center.x + half_side, self.center.y - half_side),
            Vector2D(self.center.x + half_side, self.center.y + half_side),
            Vector2D(self.center.x - half_side, self.center.y + half_side)
        ]

    def rotate(self, angle: float):
        angle_rad = math.radians(angle)
        for i in range(len(self._vertices)):
            self._vertices[i] = self._vertices[i].v_rotate(self.center, angle_rad)

class Rectangle(Shape):
    def __init__(self, config_elem: object):
        super().__init__(config_elem=config_elem)
        self.width = config_elem.get("width", 1.0)
        self.length = config_elem.get("length", 1.0)
        self.set_vertices()

    def configure(self, width: float, length: float, new_center: Vector2D):
        super().__init__(new_center)
        self.width = width
        self.length = length
        self.set_vertices()

    def area(self):
        return self.width * self.length

    def perimeter(self):
        return 2 * (self.width + self.length)

    def vertices(self):
        return self._vertices

    def set_center(self, new_center: Vector2D):
        super().set_center(new_center)
        self.set_vertices()

    def set_vertices(self):
        half_width = self.width * 0.5
        half_length = self.length * 0.5
        self._vertices = [
            Vector2D(self.center.x - half_width, self.center.y - half_length),
            Vector2D(self.center.x + half_width, self.center.y - half_length),
            Vector2D(self.center.x + half_width, self.center.y + half_length),
            Vector2D(self.center.x - half_width, self.center.y + half_length)
        ]

    def rotate(self, angle: float):
        angle_rad = math.radians(angle)
        for i in range(len(self._vertices)):
            self._vertices[i] = self._vertices[i].v_rotate(self.center, angle_rad)
class Triangle(Shape):
    def __init__(self, config_elem:dict):
        super().__init__(config_elem=config_elem)
        angle1 = config_elem.get("angle1", 60)
        angle2 = config_elem.get("angle2", 60)
        hypotenuse = config_elem.get("hypotenuse", 1)
        if angle1 + angle2 >= 180:
            raise ValueError("The sum of the two angles must be less than 180 degrees")
        self.hypotenuse = hypotenuse
        self.angle1 = math.radians(angle1)
        self.angle2 = math.radians(angle2)
        self.angle3 = math.radians(180 - angle1 - angle2)
        self.base = hypotenuse * math.sin(self.angle1)
        self.length = hypotenuse * math.sin(self.angle2)
        self.side1 = hypotenuse * math.sin(self.angle1)
        self.side2 = hypotenuse * math.sin(self.angle2)
        self.side3 = hypotenuse
        self.set_vertices()
    
    def configure(self, hypotenuse:float, angle1:float, angle2:float, new_center: Vector2D):
        if angle1 + angle2 >= 180:
            raise ValueError("The sum of the two angles must be less than 180 degrees")
        super().__init__(new_center)
        self.hypotenuse = hypotenuse
        self.angle1 = math.radians(angle1)
        self.angle2 = math.radians(angle2)
        self.angle3 = math.radians(180 - angle1 - angle2)
        self.base = hypotenuse * math.sin(self.angle1)
        self.length = hypotenuse * math.sin(self.angle2)
        self.side1 = hypotenuse * math.sin(self.angle1)
        self.side2 = hypotenuse * math.sin(self.angle2)
        self.side3 = hypotenuse
        self.set_vertices()

    def area(self):
        return 0.5 * self.base * self.length

    def perimeter(self):
        return self.side1 + self.side2 + self.side3

    def vertices(self):
        return self._vertices

    def set_center(self, new_center: Vector2D):
        super().set_center(new_center)
        self.set_vertices()

    def set_vertices(self):
        # Assuming the triangle is right-angled for simplicity
        self._vertices = [
            Vector2D(self.center.x - self.base * 0.5, self.center.y - self.length * 0.5),
            Vector2D(self.center.x + self.base * 0.5, self.center.y - self.length * 0.5),
            Vector2D(self.center.x, self.center.y + self.length * 0.5)
        ]

    def rotate(self, angle: float):
        angle_rad = math.radians(angle)
        for i in range(len(self._vertices)):
            self._vertices[i] = self._vertices[i].v_rotate(self.center, angle_rad)
