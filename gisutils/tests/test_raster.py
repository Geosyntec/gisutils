from pkg_resources import resource_filename

import pytest
import numpy.testing as nptest

import numpy
from affine import Affine

from gisutils import raster


def test_load():
    demfile = resource_filename('gisutils.tests._data.raster', 'powell_butte.png')
    dem, meta = raster.load(demfile)

    expected_meta = {
        'transform': (649635.0, 30.0, 0.0, 4901415.0, 0.0, -30.0),
        'crs': {'init': 'epsg:26710'},
        'height': 474,
        'width': 348,
        'nodata': None,
        'driver': 'PNG',
        'count': 1,
        'affine': Affine(30.0, 0.0, 649635.0, 0.0, -30.0, 4901415.0),
        'dtype': 'uint8',
    }
    assert meta == expected_meta
    assert dem.shape == (meta['height'], meta['width'])


@pytest.fixture
def base_affine(rotation):
    return Affine.translation(5, 15) * Affine.rotation(rotation) * Affine.scale(3, -3)


@pytest.mark.parametrize(('rotation', 'xy', 'expected_rowcol'), [
    (30, (23, 13), ((3,), (4,))),
    (60, (28, 28), ((4,), (7,))),
    (45, (15, 10), ((3,), (1,))),
    (45, ((13, 19), (17, 25)), ((1, 0), (2, 5))),
])
def test_xy_to_rowcol(rotation, xy, expected_rowcol):
    x, y = xy
    affine = base_affine(rotation)
    rowcol = raster.xy_to_rowcol(x, y, affine)

    nptest.assert_array_equal(rowcol, numpy.array(expected_rowcol))


@pytest.mark.parametrize(('rotation', 'rowcol', 'expected_xy'), [
    (30, ((4,), (3,)), (18.794,  9.108)),
    (60, ((4,), (7,)), (25.892,  27.187)),
    (45, ((2,), (1,)), (11.364, 12.879)),
    (45, ((2, 5), (1, 0)), ((11.364, 15.607), (12.879, 4.393))),
])
def test_rowcol_to_xy(rotation, rowcol, expected_xy):
    affine = base_affine(rotation)
    row, col, = rowcol
    xy = raster.rowcol_to_xy(row, col, affine)

    nptest.assert_array_almost_equal(xy.ravel(), numpy.array(expected_xy).ravel(), decimal=3)
