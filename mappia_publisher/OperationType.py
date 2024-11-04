from enum import Enum

#Supported Operations
class OperationType(Enum):
    RAW = 0
    INTEGRAL = 1
    AREAINTEGRAL = 2
    MAX = 3
    AVERAGE = 4
    MIN = 5
    AREA = 6
    SUM = 7
    CELLS = 8
    RGBA = 9

    @staticmethod
    def getOptions():
        return [member for member in OperationType.__members__]

    def getName(self):
        return self.name.lower()

    def __str__(self):
        return self.name

