from shapely import geometry
import geopandas
import numpy
from affine import Affine
from gisutils import algo

def test_average_slope():
    
    _lines = [
        geometry.LineString(coordinates = [(0, 5), (10, 5)]), # across the center (slope = 1)
        geometry.LineString(coordinates = [(5, 0), (5, 10)]), # up the center (slope = 0)
        geometry.LineString(coordinates = [(0, 0), (10, 10)]), # corner to corner (slope ~0.707)
        geometry.LineString(coordinates = [(0, 0), (0, 10), (10, 10)]), # corner to corner to corner (slope = 0.5)
        geometry.LineString(coordinates = [(0, 0), (5, 5), (5, 0), (0, 0)]), # loops back to start (slope = 0)
    ]

    lines = geopandas.GeoDataFrame(geometry = _lines)
    
    expected = [
        1.000000,
        0.000000,
        0.707107,
        0.500000,
        0.000000,
    ]
    
    hill = numpy.mgrid[:11, :11][1]
    
    trans = Affine.translation(0, 10) * Affine.rotation(0) * Affine.scale(1, -1)
    
    result = algo.average_slope(lines, hill, trans)

    assert numpy.allclose(result.average_slope, expected)
