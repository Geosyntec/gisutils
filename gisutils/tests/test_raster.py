import pytest
import numpy.testing as nptest

import numpy
from affine import Affine

from gisutils import raster


@pytest.mark.parametrize(('affine', 'xy', 'expected_rowcol'), [
    (Affine(2.568, 1.500, 5, 1.500, -2.568, 15), (23, 13), ((4,), (3,))),
    (Affine(1.500, 2.568, 5, 2.568, -1.500, 15), (28, 28), ((7,), (4,))),
    (Affine(2.212, 2.212, 5, 2.212, -2.212, 15), (13, 17), ((2,), (1,))),
    (Affine(2.212, 2.212, 5, 2.212, -2.212, 15), ((13, 19), (17, 25)), ((2, 5), (1, 0))),
])
def test_xy_to_rowcol(affine, xy, expected_rowcol):
    x, y = xy
    rowcol = raster.xy_to_rowcol(x, y, affine)

    nptest.assert_array_equal(rowcol, numpy.array(expected_rowcol))


@pytest.mark.parametrize(('affine', 'rowcol', 'expected_xy'), [
    (Affine(2.568, 1.500, 5, 1.500, -2.568, 15), ((4,), (3,)), (19.772, 13.296)),
    (Affine(1.500, 2.568, 5, 2.568, -1.500, 15), ((7,), (4,)), (25.772, 26.976)),
    (Affine(2.212, 2.212, 5, 2.212, -2.212, 15), ((2,), (1,)), (11.636, 17.212)),
    (Affine(2.212, 2.212, 5, 2.212, -2.212, 15), ((2, 5), (1, 0)), ((11.636, 16.060), (17.212, 26.060))),
])
def test_rowcol_to_xy(affine, rowcol, expected_xy):
    row, col, = rowcol
    xy = raster.rowcol_to_xy(row, col, affine)

    nptest.assert_array_almost_equal(xy.ravel(), numpy.array(expected_xy).ravel())
