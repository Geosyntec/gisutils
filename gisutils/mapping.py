from contextlib import contextmanager
from functools import wraps
import warnings
import os


def check_arcpy(func):  # pragma: no cover
    """ Decorator to allow a function to take a additional keyword
    arguments related to printing status messages to stdin or as arcpy
    messages.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            global arcpy
            import arcpy
            return func(*args, **kwargs)
        except ImportError:
            raise RuntimeError('`arcpy` is not available on this system')

    return wrapper


@contextmanager
@check_arcpy
def Extension(name):
    """ Context manager to facilitate the use of ArcGIS extensions

    Inside the context manager, the extension will be checked out. Once
    the interpreter leaves the code block by any means (e.g., successful
    execution, raised exception) the extension will be checked back in.

    Examples
    --------
    >>> import gisutils, arcpy
    >>> with gisgisutils.mapping.mapping.Extension("spatial"):
    ...     arcpy.sa.Hillshade("C:/data/dem.tif")

    """

    if arcpy.CheckExtension(name) == u"Available":
        status = arcpy.CheckOutExtension(name)
        yield status
    else:
        raise RuntimeError("%s license isn't available" % name)

    arcpy.CheckInExtension(name)


@contextmanager
@check_arcpy
def OverwriteState(state):
    """ Context manager to temporarily set the ``overwriteOutput``
    environment variable.

    Inside the context manager, the ``arcpy.env.overwriteOutput`` will
    be set to the given value. Once the interpreter leaves the code
    block by any means (e.g., successful execution, raised exception),
    ``arcpy.env.overwriteOutput`` will reset to its original value.

    Parameters
    ----------
    path : str
        Path to the directory that will be set as the current workspace.

    Examples
    --------
    >>> import gisutils
    >>> with gisutils.mapping.OverwriteState(False):
    ...     # some operation that should fail if output already exists

    """

    orig_state = arcpy.env.overwriteOutput
    arcpy.env.overwriteOutput = bool(state)
    yield state
    arcpy.env.overwriteOutput = orig_state


@contextmanager
@check_arcpy
def WorkSpace(path):
    """ Context manager to temporarily set the ``workspace``
    environment variable.

    Inside the context manager, the `arcpy.env.workspace`_ will
    be set to the given value. Once the interpreter leaves the code
    block by any means (e.g., successful execution, raised exception),
    `arcpy.env.workspace`_ will reset to its original value.

    .. _arcpy.env.workspace: http://goo.gl/0NpeFN

    Parameters
    ----------
    path : str
        Path to the directory that will be set as the current workspace.

    Examples
    --------
    >>> import propagator
    >>> with gisgisutils.mapping.mapping.OverwriteState(False):
    ...     # some operation that should fail if output already exists

    """

    orig_workspace = arcpy.env.workspace
    arcpy.env.workspace = path
    yield path
    arcpy.env.workspace = orig_workspace


@check_arcpy
class EasyMapDoc(object):
    """ The object-oriented map class Esri should have made.

    Create this the same you would make any other
    `arcpy.mapping.MapDocument`_. But now, you can directly list and
    add layers and dataframes. See the two examples below.

    Has ``layers`` and ``dataframes`` attributes that return all of the
    `arcpy.mapping.Layer`_ and `arcpy.mapping.DataFrame`_ objects in the
    map, respectively.

    .. _arcpy.mapping.MapDocument: http://goo.gl/rf4GBH
    .. _arcpy.mapping.DataFrame: http://goo.gl/ctJu3B
    .. _arcpy.mapping.Layer: http://goo.gl/KfrGNa

    Attributes
    ----------
    mapdoc : arcpy.mapping.MapDocument
        The underlying arcpy MapDocument that serves as the basis for
        this class.

    Examples
    --------
    >>> # Adding a layer with the Esri version:
    >>> import arcpy
    >>> md = arcpy.mapping.MapDocument('CURRENT')
    >>> df = arcpy.mapping.ListDataFrames(md)
    >>> arcpy.mapping.AddLayer(df, myLayer, 'TOP')

    >>> # And now with an ``EasyMapDoc``:
    >>> import gisutils
    >>> ezmd = gisutils.mapping.EasyMapDoc('CURRENT')
    >>> ezmd.add_layer(myLayer)

    """

    def __init__(self, *args, **kwargs):
        try:
            self.mapdoc = arcpy.mapping.MapDocument(*args, **kwargs)
        except RuntimeError:
            self.mapdoc = None

    @property
    def layers(self):
        """
        All of the layers in the map.
        """
        return arcpy.mapping.ListLayers(self.mapdoc)

    @property
    def dataframes(self):
        """
        All of the dataframes in the map.
        """
        return arcpy.mapping.ListDataFrames(self.mapdoc)

    def findLayerByName(self, name):
        """ Finds a `layer`_ in the map by searching for an exact match
        of its name.

        .. _layer: http://goo.gl/KfrGNa

        Parameters
        ----------
        name : str
            The name of the layer you want to find.

        Returns
        -------
        lyr : arcpy.mapping.Layer
            The map layer or None if no match is found.

        .. warning:: Group Layers are not returned.

        Examples
        --------
        >>> import gisutils
        >>> ezmd = gisutils.mapping.EasyMapDoc('CURRENT')
        >>> wetlands = ezmd.findLayerByName("wetlands")
        >>> if wetlands is not None:
        ...     # do something with `wetlands`

        """

        for lyr in self.layers:
            if not lyr.isGroupLayer and lyr.name == name:
                return lyr

    def add_layer(self, layer, df=None, position='top'):
        """ Simply adds a `layer`_ to a map.

        .. _layer: http://goo.gl/KfrGNa

        Parameters
        ----------
        layer : str or arcpy.mapping.Layer
            The dataset to be added to the map.
        df : arcpy.mapping.DataFrame, optional
            The specific dataframe to which the layer will be added. If
            not provided, the data will be added to the first dataframe
            in the map.
        position : str, optional ('TOP')
            The positional within `df` where the data will be added.
            Valid options are: 'auto_arrange', 'bottom', and 'top'.

        Returns
        -------
        layer : arcpy.mapping.Layer
            The successfully added layer.

        Examples
        --------
        >>> import gisutils
        >>> ezmd = gisutils.mapping.EasyMapDoc('CURRENT')
        >>> watersheds = gisutils.load_data("C:/gis/hydro.gdb/watersheds")
        >>> ezmd.add_layer(watersheds)

        """

        # if no dataframe is provided, select the first
        if df is None:
            df = self.dataframes[0]

        # check that the position is valid
        valid_positions = ['auto_arrange', 'bottom', 'top']
        if position.lower() not in valid_positions:
            raise ValueError('Position: %s is not in %s' % (position.lower, valid_positions))

        # layer can be a path to a file. if so, convert to a Layer object
        layer = load_data(layer, 'layer')

        # add the layer to the map
        arcpy.mapping.AddLayer(df, layer, position.upper())

        # return the layer
        return layer