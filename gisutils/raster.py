import numpy
from affine import Affine
import rasterio

from gisutils import validate


def load(rasterfile, bands=None):
    if bands is None:
        bands = 0

    with rasterio.open(rasterfile, 'r') as r:
        meta = r.meta
        data = r.read()

    return data[0, :, :], meta


def rowcol_to_xy(rows, cols, affine):
    """
    Convert (rows, cols) raster row and column indices to geographic
    coordinates based on the affine transformation of the raster.

    Parameters
    ----------
    rows, cols : array-like
        One dimensional arrays representing the row and column indices
        to be converted to real-world coordinates.
    affine : affine.Affine or numpy array
        The affine object or a 3x3 numpy array that defines the
        transformation.

    Returns
    -------
    xy : array
        An Nx2 array of the x- and y- coordinates. This can be unpacked
        into the individual sets.

    Examples
    --------
    >>> from affine import Affine
    >>> from gisutils import raster
    >>> translate = Affine.translation(5, 15)
    >>> rotate = Affine.rotation(30)
    >>> scale = Affine.scale(3, -3)
    >>> transformation = translate * rotate * scale
    >>> x, y = raster.rowcol_to_xy([2, 4, 5, 7], [8, 3, 4, 4], transformation)
    >>> print(x)
    [ 27.28460969  18.79422863  22.89230485  25.89230485]

    >>> print(y)
    [ 24.40192379   9.10769515   8.00961894   2.81346652]

    """

    # make it a 3x3 matrix
    aff_array = numpy.array(affine).reshape((3, 3))

    # check that rows amd cols are indeed 1-D vectors
    rows = validate.is_vector(rows)
    cols = validate.is_vector(cols)

    # filler
    layers = numpy.ones_like(rows)
    vector = numpy.array([cols, rows, layers])

    # compute xy
    xy = numpy.dot(aff_array, vector)[:2, :]
    return xy


def xy_to_rowcol(x, y, affine):
    """
    Convert (x, y) coordinates to raster column and row indices based on
    the affine transformation of the raster.

    Parameters
    ----------
    x, y : array-like
        One dimensional arrays representing the x and y coorindates
        to be converted to raster/array indicesraste.
    affine : affine.Affine or numpy array
        The affine object or a 3x3 numpy array that defines the
        transformation.

    Returns
    -------
    rowcol : array
        An Nx2 array of the row- and column- indices. This can be
        unpacked into the individual sets.

    Examples
    --------
    >>> from affine import Affine
    >>> from gisutils import raster
    >>> translate = Affine.translation(5, 15)
    >>> rotate = Affine.rotation(30)
    >>> scale = Affine.scale(3, -3)
    >>> transformation = translate * rotate * scale
    >>> x = [ 29.,  19.,  23.,  26.]
    >>> y = [ 22.,   9.,   8.,   3.]
    >>> raster.xy_to_rowcol(x, y, transformation)
    array([[1, 4, 5, 6],
           [8, 3, 4, 4]])

    """
    # affine might be an Affine object, might be 3x3 array or
    # 9-element vector. Let's first make damn sure is a 9-element
    # vector
    aff_array = numpy.array(affine).reshape(9)

    # now be damn sure we have an Affine object, and reverse it to
    # go from coordinates to indices
    affine = ~Affine(*aff_array[:6])

    # compute the y, x values
    yx = numpy.floor(rowcol_to_xy(y, x, affine))

    # convert to int and flip to xy
    xy = yx.astype(int)[::-1]
    return xy
