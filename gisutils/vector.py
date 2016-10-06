import numpy
from scipy import interpolate
import pandas
import geopandas

from gisutils import validate


def load(filename):
    """
    Loads the points of interest for the analysis.

    Parameters
    ----------
    filename : str
        Path to the filename containing the points of interest.

    Returns
    -------
    POI : pandas.DataFrame
        A dataframe containing the coordinates and meta data describing
        the the points of interest.
    meta : dict
        Metadata related to the filename.

    """

    df = geopandas.read_file(filename)
    return df, {'crs': df.crs}


def line_to_df(geom, **gdfopts):
    """
    Converts a line geometry to a dataframe of x/y coordinates

    Parameters
    ----------
    geom : shapely line geometry
    **gdfopts : keyword arguments
        Other parameters passed directing to the
        ``geopandas.GeoDataFrame`` constructor.

    Returns
    -------
    gdf : geopandas.GeoDataFrame

    Examples
    --------
    >>> from shapely import geometry
    >>> geom = geometry.LineString([[0., 0.], [1., 0.], [1., 1.]])
    >>> vector.line_to_df(geom)

    """

    xy = numpy.array(geom.xy).T
    df = pandas.DataFrame(xy, columns=['x', 'y'])
    return geopandas.GeoDataFrame(df, **gdfopts)


def _linear_distance(df, xcol, ycol):
    """
    Computes the distance along an x-y dataframe
    """
    _dist = numpy.sqrt((df[xcol] - df[xcol].shift())**2 + (df[ycol] - df[ycol].shift())**2)
    dist = pandas.Series(_dist).fillna(0).cumsum()
    return dist


def interpolate_coord(df, xcol, ycol, step, distcol='d'):
    """
    Interpolates x/y coordinates along a line at a fixed distance.

    Parameters
    ----------
    df : pandas.DataFrame
    xcol, ycol : str
        Labels of the columns in ``df`` containing the x- and y-coords,
        respectively.
    step : int
        The spacing between the interpolated points.
    distcol : string, optional (default = 'd')
        Label of the column where the distance along the line is stored.

    Returns
    -------
    pandas.DataFrame

    """

    dist = _linear_distance(df, xcol, ycol)

    d_ = numpy.arange(0, numpy.floor(dist.max()), step)

    x_interp = interpolate.interp1d(dist, df[xcol])
    y_interp = interpolate.interp1d(dist, df[ycol])

    return pandas.DataFrame({'d': d_, 'x': x_interp(d_), 'y': y_interp(d_)})
