# ------------------------------------------------------------------------------
# File: modules/shapes.py
# Description: Contains data classes for polygons, points, etc.
# ------------------------------------------------------------------------------


class PointData:
    """Holds x, y coords of a point."""

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        """Needed to compare points."""
        if isinstance(other, PointData):
            return self.x == other.x and self.y == other.y
        return False

    def __ne__(self, other):
        return not self.__eq__(other)


class PolygonData:
    """
    Holds a list of points (2 for bounding box), a color, and a class ID.
    """

    def __init__(self, points, color, class_id=None):
        self.points = points  # list of PointData
        self.color = color
        self.class_id = class_id
