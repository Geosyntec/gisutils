import numpy
from scipy import interpolate
import pandas
import geopandas
from shapely import geometry

from gisutils import validate


def load(data_source):
    """
    Loads the a geospatial data source.

    Parameters
    ----------
    data_source : str
        Path to the geospatial data.

    Returns
    -------
    gdf : geopandas.GeoDataFrame
        A dataframe containing the coordinates and meta data
        describing the the points of interest.
    meta : dict
        Metadata related to the data.

    """

    gdf = geopandas.read_file(data_source)
    return gdf, {'crs': gdf.crs}


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


def _explode_geom(row):
    # save each geo part in its own row
    gsr = geopandas.GeoSeries([
        poly for poly in geometry.shape(row['geometry'])
    ])
    meta = row['properties']
    return geopandas.GeoDataFrame(meta, geometry=gsr, index=gsr.index)


def explode(src):
    dst = (
        pandas.concat(
            [_explode_geom(row) for row in src.iterfeatures()],
            ignore_index=True
        ).pipe(geopandas.GeoDataFrame)
    )
    return dst


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


def glue_lines_together(gdf, seed_id, id_col, geom_col='geometry', max_tries=None):
    """
    Create a contiguous line from an unordered sequence of touching segments

    Parameters
    ----------
    gdf : geopandas.GeoDataFrame
    seed_id : string or number
        A unique value found in `id_col` to select the starting segment for
        the final line.
    id_col : string
        Name of the column in `gdf` that uniquely identifies each segment.
    geom_col : string, optional (default = 'geometry')
        Name of the goemetry column in `gdf`.
    max_tries : int, optional
        Number of iterations to try to place all of the segments. Defaults
        to the twice the number of rows in `gdf`, acting as a backstop
        to preventa boundless loop in case of a gap in the segments. However,
        you can use this to limit the connections of the first *N* segments.

    Returns
    -------
    line : shapely.geometry.LineString
        The contiguous line built from the individual segments.
    extra_geoms : geopandas.GeoDataFrame
        A GeoDataFrame of any geometries that could not be attached to the
        final line.

    Notes
    -----
    Conditions assumed for this function:

      * Subsequent sections must be touching. E.g., seg1.touches(seg2) is True.
      * Each section touches no more than two other segments (the one before
        and the one after).
      * All of your segments need to be oriented in the same direction
      * If you pick wrong the end of the line as the seed, the final line will
        have several discontinuities where the wrong ends of the segments are
        attached. To prevent this, seed with the other end of the line.

    Examples
    --------
    import geopandas
    from shapely import geometry
    from gisutils import vector
    gdf = geopandas.GeoDataFrame(
        data={'segment': [1, 2, 3]},
        geometry=[
            geometry.LineString([(0, 0), (10, 10)]),
            geometry.LineString([(10, 20), (30, 30)]),
            geometry.LineString([(10, 10), (10, 20)]),
        ]
    )

    line, extras = vector.glue_lines_together(segments_gdf, seed, 'segment')
    print(extras.shape)
    print(line)

    """

    tries = 0
    success = 0
    if max_tries is None:
        max_tries = gdf.shape[0] * 2

    geoms = (
        gdf.select(lambda c: c in [id_col, geom_col], axis='columns')
           .set_index(id_col)
    )

    line = geoms.loc[seed_id, geom_col]
    extra_geoms = geoms.drop(seed_id, axis='index')
    while extra_geoms.shape[0] > 0 and tries < max_tries:
        tries += 1
        next_geom = extra_geoms.loc[extra_geoms.touches(line), 'geometry']

        if next_geom.shape[0] != 1:
            msg = 'Found {} intersections for {}'
            raise ValueError(msg.format(next_geom.shape[0], next_geom))
        else:
            all_coords = [line.coords, next_geom.values[0].coords]
            line = geometry.LineString([
                xy
                for xy_pairs in all_coords
                for xy in xy_pairs
            ])
            extra_geoms = extra_geoms.drop(next_geom.index[0], axis='index')
            success += 1

    return line, extra_geoms
