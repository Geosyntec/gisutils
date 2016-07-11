import numpy
import rasterio

from gisutils import validate

def load(rasterfile, bands=None):
    if bands is None:
        bands = 0

    with rasterio.open(rasterfile, 'r') as raster:
        meta = raster.meta
        data = raster.read()

    return data[0, :, :], meta


def rowcol_to_xy(rows, cols, affine):
    """
    Convert (rows, cols) raster column and row indices to coordinates based
    on the affine transformation of the raster.
    """
    # make it a 3x3 matrix
    Affine = numpy.array(affine).reshape((3, 3))

    # filler
    layers = numpy.ones_like(rows)
    vector = numpy.array([rows, cols, layers])

    xy = numpy.dot(Affine, vector)[:2, :]
    return xy


def xy_to_rowcol(x, y, affine):
    """
    Convert (x, y) coordinates to raster column and row indices based on
    the affine transformation of the raster.


    Paramaters
    ----------
    x, y : float
        Easting/Northing (lon/lat) coorindates to be transformed.
    affine : numpy array (3-by-3) or ``affine.Affine`` object.
        See notes below for more information

    Returns
    -------
    rowcol : array of ints
        The row and column indicies of the pixel in the raster
        corresponding to ``x`` and ``y``.

    Notes
    -----
    Effectively, this uses numpy to solve the linear algebra problem

    .. math::

        t = Av

    Where ``t`` is transformed column vector with elements ``[x, y, 1]``
    and A is the matrix that defines the affine transformation:

    .. code::

        | a  b  c |
        | d  e  f |
        | 0  0  1 |

    Where:

        a : rate of change of X with respect to increasing column,
            i.e. pixel width.
        b : rotation, 0 if the raster is oriented "north up".
        c : X coordinate of the top left corner of the top left pixel.
        d : rotation, 0 if the raster is oriented "north up".
        e : rate of change of Y with respect to increasing row,
            usually a negative number (i.e. -1 * pixel height) if
            north-up.
        f : Y coordinate of the top left corner of the top left pixel.

    The result is a column vector with the elements ``[row, col, 1]``

    Where:

        row : row index of the nearest pixel.
        col : column index of the nearest pixel.

    """

    x = validate.is_vector(x)
    y = validate.is_vector(y)
    ones = numpy.ones_like(x)

    # make in a 3x3 matrix
    Affine = numpy.array(affine).reshape((3, 3))

    # make a 3x1 vector
    transformed = numpy.array([x, y, ones])

    # solve the system
    vector = numpy.linalg.solve(Affine, transformed)

    # return whole number index
    rowcol = numpy.floor(vector).astype(int)[:2, :]
    return rowcol