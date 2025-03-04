import math

class Vector2D:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector2D(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        return Vector2D(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar):
        return Vector2D(self.x / scalar, self.y / scalar)

    def magnitude(self):
        return math.sqrt(self.x**2 + self.y**2)

    def normalize(self):
        mag = self.magnitude()
        if mag == 0:
            return Vector2D()
        return Vector2D(self.x / mag, self.y / mag)

    def dot(self, other):
        return self.x * other.x + self.y * other.y

    def v_rotate(self, point, angle_rad:float):
        # Translate the vector to the origin
        translated = self - point
        # Rotate the translated vector
        cos_theta = math.cos(angle_rad)
        sin_theta = math.sin(angle_rad)
        x_new = translated.x * cos_theta + translated.y * sin_theta
        y_new = -translated.x * sin_theta + translated.y * cos_theta
        rotated = Vector2D(x_new, y_new)
        return rotated + point

    def translate(self, dx:float, dy:float):
        return Vector2D(self.x + dx, self.y + dy)

    def __repr__(self) -> str:
        return f"Vector2D({self.x}, {self.y})"

def rad_to_deg(rad:float) -> float:
    return rad * (180.0 / math.pi)

def deg_to_rad(deg:float) -> float:
    return deg * (math.pi / 180.0)