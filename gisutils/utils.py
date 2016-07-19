"""
General utilities
"""

import os


def add_suffix_to_filename(filename, suffix):
    """
    Adds a suffix to a(n output) filename.

    Parameters
    ----------
    filename : str or a list of str
        The filename that needs a suffix.
    suffix : str
        The suffix to be added.

    Returns
    -------
    new_filename : str
        The original filename with followed by an underscore, the
        suffix, and then any extension that the original filename had.

    Examples
    --------
    >>> from gitutils import utils
    >>> utils.add_suffix_to_filename('test_shapefile.shp', 'try_2')
    'test_shapefile_try_2.shp'

    >>> utils.add_suffix_to_filename('test_layer', 'try_2')
    'test_layer_try_2'

    >>> utils.add_suffix_to_filename(['streams.shp', 'locations.shp'])

    """
    name, extension = os.path.splitext(filename)
    return '{}_{}{}'.format(name, suffix, extension)


def find_row_in_array(array, column, value):
    """
    Find a single row in a record array.

    Parameters
    ----------
    array : numpy.recarray
        The record array to be searched.
    column : str
        The name of the column of the array to search.
    value : int, str, or float
        The value sought in ``column``

    Raises
    ------
    ValueError
        An error is raised if more than one row is found.

    Returns
    -------
    row : numpy.recarray row
        The found row from ``array``.

    Examples
    --------
    >>> from gisutils import utils
    >>> import numpy
    >>> x = numpy.array(
            [
                ('A1', 'Ocean', 'A1_x'), ('A2', 'Ocean', 'A2_x'),
                ('B1', 'A1', 'None'), ('B2', 'A1', 'B2_x'),
            ], dtype=[('ID', '<U5'), ('DS_ID', '<U5'), ('Cu', '<U5'),]
        )
    >>> utils.find_row_in_array(x, 'ID', 'A1')
    ('A1', 'Ocean', 'A1_x', 'A1_y')

    """

    rows = list(filter(lambda x: x[column] == value, array))
    if len(rows) == 0:
        row = None
    elif len(rows) == 1:
        row = rows[0]
    else:
        raise ValueError("more than one row where {} == {}".format(column, value))

    return row