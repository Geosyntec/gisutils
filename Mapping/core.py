import arcpy


class Extension(object):
    """ Basic context manager for ArcGIS extensions

    When used in conjunction with a ``with`` statement,
    this will automatically check extensions in and out
    without ``try/except`` blocks regardless if you
    encounter errors.

    Parameters
    ----------
    name : str
        The ArcGIS/arcpy-appropriate string representation
        of the extension.

    Example
    -------
    >>> import gisutils
    >>> with gisutils.Extension("spatial") as ext:
    >>> ... # spatial analyst is automatically checked out
    >>> ... # do some spatial analyst stuff
    >>> # SA is automatically checked back in once you exit
    """
    def __init__(self, name):
        self.name = name

    def __enter__(self):
        arcpy.CheckOutExtension(self.name)

    def __exit__(self, *args):
        arcpy.CheckOutExtension(self.name)


class OverwriteState(object):
    """ Manage the overwrite output state of arcpy

    Sometimes you want to set overwriteOutput = True
    for a brief set of operations, but don't want to
    permanently change it and maybe don't even know
    what the current state is.

    This context manager caches the existing value
    of ``arcpy.env.overwriteOutput``, sets it to
    the value you need, and then restores it.

    Parameters
    ----------
    overwrite : bool
        The desired, temporary state of ``arcpy.env.overwriteOutput``

    Example
    -------
    >>> import gisutils
    >>> arcpy.env.overwriteOutput = False # permanent state
    >>> with gisutils.OverwriteState(True) as state:
    >>> ... print(arcpy.env.overwriteOutput)
    >>> ... # do stuff
    True
    >>> # then once we're out of the with block:
    >>> print(arcpy.env.overwriteOutput)
    False

    """

    def __init__(self, overwrite):
        self.orig_state = arcpy.env.overwriteOutput
        self.new_state = bool(overwrite)

    def __enter__(self, *args, **kwargs):
        arcpy.env.overwriteOutput = self.new_state

    def __exit__(self, *args, **kwargs):
        arcpy.env.overwriteOutput = self.orig_state


class EasyMapDoc(object):
    """ Easy-to-use, extenisble map document

    arcpy.mapping.MapDocuments are a pain in the ass.
    You'd think you'd be able to do something like:
    >>> mapdoc = arcpy.mapping.MapDocument("CURRENT")
    >>> layers = mapdoc.get_layers() # fails

    But instead you have to do:
    >>> mapdoc = arcpy.mapping.MapDocument("CURRENT")
    >>>  arcpy.mapping.ListLayers(mapdoc)

    That's dumb. The whole point of having a class is
    to persist, or at least make convenient the data
    that is associated with it. So that's what this
    class does. And it uses properties so that when
    you try to access, e.g. the layers, they are
    always refreshed.

    Parameters
    ----------
    args
        Positional arguments fed directly to
        arcpy.mapping.MapDocument
    kwargs
        Keyword arguments fed directly to
        arcpy.mapping.MapDocument

    Example
    -------
    >>> import gisutils
    >>> path_to_new_layer = "<somepath>"
    >>> mapdoc = gisutils.EasyMapDoc("CURRENT")
    >>> mapdoc.layers
    >>> # [<list of N layers>]
    >>> layer = mapdoc.add_layer(path_to_new_layer)
    >>> mapdoc.layers
    >>> # [<list of N+1 layers>]
    >>> mapdoc.mapdocument
    >>> # the actual arcpy.mapping.MapDocument object

    """

    def __init__(self, *args, **kwargs):
        self.mapdocument = arcpy.mapping.MapDocument(*args, **kwargs)

    @property
    def layers(self):
        return arcpy.mapping.ListLayers(self.mapdocument)

    @property
    def dataframes(self):
        return arcpy.mapping.ListDataFrames(self.mapdocument)

    def findLayerByName(self, name):
        """ Finds and returns a layer in a map

        Parameters
        ----------
        name : str
            The name of the layer

        Returns
        -------
        lyr : arcpy.mapping.Layer, or None
            The arcpy layer, if found. Otherwise None is returned.

        """

        for lyr in self.layers:
            if not lyr.isGroupLayer and lyr.datasetName == name:
                return lyr

    def add_layer(self, layer, df=None, position='top'):
        """ Add a layer to a map

        Parameters
        ----------
        layer : str or arcpy.mapping.Layer
            The name of the layer or the layer object itself

        Returns
        -------
        lyr : arcpy.mapping.Layer, or None
            The arcpy layer, if found. Otherwise None is returned.

        """

        # if no dataframe is provided, select the first
        if df is None:
            df = self.dataframes[0]

        # check that the position is valid
        valid_positions = ['auto_arrange', 'bottom', 'top']
        if position.lower() not in valid_positions:
            raise ValueError('Position: %s is not in %s' % (position.lower, valid_positions))

        # layer can be a path to a file. if so, convert to a Layer object
        if isinstance(layer, basestring):
            layer = arcpy.mapping.Layer(layer)

        # add the layer to the map
        arcpy.mapping.AddLayer(df, layer, position.upper())

        # return the layer
        return layer
