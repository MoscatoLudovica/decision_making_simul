import math

class Vector3D:
    def __init__(self, x:float=0, y:float=0, z:float=0):
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, other):
        return Vector3D(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vector3D(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar):
        return Vector3D(self.x * scalar, self.y * scalar, self.z * scalar)

    def __truediv__(self, scalar):
        return Vector3D(self.x / scalar, self.y / scalar, self.z / scalar)

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other):
        return Vector3D(self.y * other.z - self.z * other.y,
                        self.z * other.x - self.x * other.z,
                        self.x * other.y - self.y * other.x)

    def magnitude(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def normalize(self):
        mag = self.magnitude()
        if mag == 0:
            return Vector3D()
        return self / mag

    def translate(self, dx:float, dy:float, dz:float):
        return Vector3D(self.x + dx, self.y + dy, self.z + dz)

    def v_rotate_x(self, point, angle:float):
        translated = self - point
        cos_theta = math.cos(angle)
        sin_theta = math.sin(angle)
        y = translated.y * cos_theta - translated.z * sin_theta
        z = translated.y * sin_theta + translated.z * cos_theta
        rotated = Vector3D(translated.x, y, z)
        return rotated + point

    def v_rotate_y(self, point, angle:float):
        translated = self - point
        cos_theta = math.cos(angle)
        sin_theta = math.sin(angle)
        x = translated.x * cos_theta + translated.z * sin_theta
        z = -translated.x * sin_theta + translated.z * cos_theta
        rotated = Vector3D(x, translated.y, z)
        return rotated + point

    def v_rotate_z(self, point, angle:float):
        translated = self - point
        cos_theta = math.cos(angle)
        sin_theta = math.sin(angle)
        x = translated.x * cos_theta - translated.y * sin_theta
        y = translated.x * sin_theta + translated.y * cos_theta
        rotated = Vector3D(x, y, translated.z)
        return rotated + point

    def __repr__(self) -> str:
        return f"Vector3D({self.x}, {self.y}, {self.z})"

def rad_to_deg(radians) -> float:
    return radians * (180.0 / math.pi)

def deg_to_rad(degrees) -> float:
    return degrees * (math.pi / 180.0)