import numpy

from gisutils import raster


def _get_nth_points_in_lines(gdf, pt_index):
    x1 = gdf['geometry'].apply(lambda g: g.coords[pt_index][0])
    y1 = gdf['geometry'].apply(lambda g: g.coords[pt_index][1])
    return x1, y1


def average_slope(gdf, dem, dem_affine, absolute=True, as_pct=True):
    """
    Computes the average slope between the first and last coordinates of
    a line using the elevations from a reference Digital Elevation Map.

    Returns an `average_slope` GeoSeries (float) containing the result
    of the slope calculation.

    Parameters
    ----------
    gdf : geopandas.GeoDataFrame
        A geodataframe of simple line geometries.
    dem : array
        Numeric array representing the digitize elevations of the area
        of interest.
    dem_affine : affine.Affine
        The affine transformation that places the DEM at the correct
        location, scale, and rotation in geographic coordinates.
    absolute : bool, optional
        If True (default), the absolute value of the slope is returned.

    Returns
    -------
    slope : geopandas.GeoSeries

    Notes
    -----
    The input parameters need to to be in the same coordinate reference
    system. This function does not reproject the information in any way.

    """

    # coords of the starts of the line
    x1, y1 = _get_nth_points_in_lines(gdf, 0)
    r1, c1 = raster.xy_to_rowcol(x1, y1, dem_affine)

    # coords of the ends of the lines
    x2, y2 = _get_nth_points_in_lines(gdf, -1)
    r2, c2 = raster.xy_to_rowcol(x2, y2, dem_affine)

    slope = (dem[r2, c2] - dem[r1, c1]) / gdf['geometry'].length
    if absolute:
        slope = numpy.abs(slope)

    factor = 1
    if as_pct:
        factor = 100

    return slope * factor

def compute_sinuosity(gdf):
    """
    Computes the sinuosity between the first and last coordinates of
    a line.

    Returns a `sinuosity` GeoSeries (float) containing the result
    of the sinuosity calculation.

    Parameters
    ----------
    gdf : geopandas.GeoDataFrame
        A geodataframe of simple line geometries.

    Returns
    -------
    sinuosity : geopandas.GeoSeries

    Notes
    -----
    The input parameters need to to be in the same coordinate reference
    system. This function does not reproject the information in any way.

    """

    # coords of the starts of the line
    x1, y1 = _get_nth_points_in_lines(gdf, 0)


    # coords of the ends of the lines
    x2, y2 = _get_nth_points_in_lines(gdf, -1)

    dx = x2.values-x1.values
    dy = y2.values-y1.values

    distance = ((dx)**2 + (dy)**2)**.5

    sinuosity = numpy.abs(gdf['geometry'].length / distance)

    return sinuosity
