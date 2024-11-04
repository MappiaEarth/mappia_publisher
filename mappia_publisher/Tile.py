# From Tiles XYZ algorithm
from .CoordinateUtils import CoordinateUtils


class Tile:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def extent(self):
        lat1, lon1 = CoordinateUtils.num2deg(self.x, self.y, self.z)
        lat2, lon2 = CoordinateUtils.num2deg(self.x + 1, self.y + 1, self.z)
        return [lon1, lat2, lon2, lat1]
