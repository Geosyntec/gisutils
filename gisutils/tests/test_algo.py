from shapely import geometry
import pandas
import geopandas
import numpy
from affine import Affine

from gisutils import algo

import pandas.util.testing as pdtest


def test_average_slope():
    _lines = [
        geometry.LineString(coordinates=[(0, 5), (10, 5)]),
        geometry.LineString(coordinates=[(5, 0), (5, 10)]),
        geometry.LineString(coordinates=[(0, 0), (10, 10)]),
        geometry.LineString(coordinates=[(0, 0), (0, 10), (10, 10)]),
        geometry.LineString(coordinates=[(0, 0), (5, 5), (5, 0), (0, 0)]),
    ]

    lines = geopandas.GeoDataFrame(geometry=_lines)

    expected = pandas.Series([
        1.000000,
        0.000000,
        0.707107,
        0.500000,
        0.000000,
    ]) * 100

    hill = numpy.mgrid[:11, :11][1]
    trans = Affine.translation(0, 10) * Affine.rotation(0) * Affine.scale(1, -1)
    result = algo.average_slope(lines, hill, trans)

    pdtest.assert_series_equal(result, expected)


def test_compute_sinuosity():
    _lines = [
        geometry.LineString(coordinates=[(0, 5), (10, 5)]),
        geometry.LineString(coordinates=[(0, 0), (0, 10), (10, 10)]),
        geometry.LineString(coordinates=[(0, 0), (5, 5), (5, 0), (0, 0)]),
    ]

    lines = geopandas.GeoDataFrame(geometry=_lines)

    expected = pandas.Series([
        1.000000,
        1.414213,
        numpy.inf,
    ])

    result = algo.compute_sinuosity(lines)

    pdtest.assert_series_equal(result, expected)
