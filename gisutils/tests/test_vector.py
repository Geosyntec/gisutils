from pkg_resources import resource_filename

import pytest
import numpy.testing as nptest
import pandas.util.testing as pdtest

import numpy
import pandas
from shapely import wkt
from shapely import geometry
import geopandas

from gisutils import vector


@pytest.fixture
def basic_xy():
    df = pandas.DataFrame({
        'x': [0., 1., 1., 5.],
        'y': [0., 0., 3., 3.]
    })
    return df


@pytest.fixture
def segments_gdf():
    gdf = geopandas.GeoDataFrame(
        data={'segment': [1, 2, 3]},
        geometry=[
            geometry.LineString([(0, 0), (10, 10)]),
            geometry.LineString([(10, 20), (30, 30)]),
            geometry.LineString([(10, 10), (10, 20)]),
        ]
    )
    return gdf


def test_load():
    shpfile = resource_filename('gisutils.tests._data.vector', 'pipelines.shp')
    shp, meta = vector.load(shpfile)

    expected_meta = {
        'crs': {'init': 'epsg:26710'},
    }
    assert meta == expected_meta
    assert isinstance(shp, geopandas.GeoDataFrame)


def test_line_to_df():
    expected = geopandas.GeoDataFrame({'x': [0., 1., 1.], 'y': [0., 0., 1.]})

    geom = geometry.LineString([[0., 0.], [1., 0.], [1., 1.]])
    result = vector.line_to_df(geom)

    pdtest.assert_frame_equal(result, expected)


def test__linear_distance(basic_xy):
    result = vector._linear_distance(basic_xy, 'x', 'y')
    expected = pandas.Series([0., 1., 3., 4.]).cumsum()
    pdtest.assert_series_equal(result, expected)


def test_interpolate_coord(basic_xy):
    result = vector.interpolate_coord(basic_xy, 'x', 'y', 1)
    expected = pandas.DataFrame({
        'd': numpy.arange(8, dtype=float),
        'x': [0., 1., 1., 1., 1., 2., 3., 4.],
        'y': [0., 0., 1., 2., 3., 3., 3., 3.]
    })
    pdtest.assert_frame_equal(result, expected)


@pytest.mark.parametrize(('seed', 'expected_pairs', 'with_extra'), [
    (1, '0.0 0.0, 10.0 10.0, 10.0 10.0, 10.0 20.0, 10.0 20.0, 30.0 30.0', False),
    (2, '10.0 20.0, 30.0 30.0, 10.0 10.0, 10.0 20.0, 0.0 0.0, 10.0 10.0', False),
    (1, '0.0 0.0, 10.0 10.0, 10.0 10.0, 10.0 20.0, 10.0 20.0, 30.0 30.0', True),
])
def test_glue_lines_together_basic(segments_gdf, seed, expected_pairs, with_extra):
    gstr = 'LINESTRING ({})'.format(expected_pairs)
    expected = wkt.loads(gstr)

    # check that an unattached segment is dropped
    if with_extra:
        line = geometry.LineString([(50, 50), (50, 50)])
        segments_gdf = pandas.concat([
            segments_gdf,
            geopandas.GeoDataFrame(data={'segment': [4]}, geometry=[line])
        ], ignore_index=True)
        with pytest.raises(ValueError):
            result, gdf = vector.glue_lines_together(segments_gdf, seed, 'segment')

    else:
        result, gdf = vector.glue_lines_together(segments_gdf, seed, 'segment')
        assert result.equals(expected)
        assert isinstance(gdf, geopandas.GeoDataFrame)
        assert gdf.shape[0] == 0
