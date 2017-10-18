from shapely import geometry
import pandas
import geopandas
import numpy
from affine import Affine

from gisutils import algo

import numpy.testing as nptest
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


def test_bearing_from_north():
    gdf = geopandas.GeoDataFrame(
        data=[1, 2, 3, 4, 5],
        geometry=[
            geometry.Point(0, 0),
            geometry.Point(2, 2),
            geometry.Point(4, 0),
            geometry.Point(2, -2),
            geometry.Point(0, 0)
        ]
    )

    result = algo.bearing_from_north(gdf)
    expected = numpy.array((numpy.nan, 1, 3, 5, 7)) * numpy.pi / 4
    nptest.assert_array_equal(result, expected)
