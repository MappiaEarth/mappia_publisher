# From Tiles XYZ algorithm
from .CoordinateUtils import CoordinateUtils

class MetaTile:
    def __init__(self):
        # list of tuple(row index, column index, Tile)
        self.tiles = []

    def add_tile(self, row, column, tile):
        self.tiles.append((row, column, tile))

    def rows(self):
        return max([r for r, _, _ in self.tiles]) + 1

    def columns(self):
        return max([c for _, c, _ in self.tiles]) + 1

    def extent(self):
        _, _, first = self.tiles[0]
        _, _, last = self.tiles[-1]
        lat1, lon1 = CoordinateUtils.num2deg(first.x, first.y, first.z)
        lat2, lon2 = CoordinateUtils.num2deg(last.x + 1, last.y + 1, first.z)
        return [lon1, lat2, lon2, lat1]
