import numpy
from matplotlib import pyplot


def is_vector(x):
    if numpy.isscalar(x):
        x = [x]

    return numpy.asarray(x).ravel()


def mpl_axes(ax, fallback='new'):
    """ Checks if a value if an Axes. If None, a new one is created or
    the 'current' one is found.
    Parameters
    ----------
    ax : matplotlib.Axes or None
        The value to be tested.
    fallback : str, optional
        If ax is None. ``fallback='new'`` will create a new axes and
        figure. The other option is ``fallback='current'``, where the
        "current" axes are return via ``pyplot.gca()``
    Returns
    -------
    fig : matplotlib.Figure
    ax : matplotlib.Axes
    """

    if ax is None:
        if fallback == 'new':
            fig, ax = pyplot.subplots()
        elif fallback == 'current':
            ax = pyplot.gca()
            fig = ax.figure
        else:
            raise ValueError("fallback must be either 'new' or 'current'")

    elif isinstance(ax, pyplot.Axes):
        fig = ax.figure

    else:
        msg = "`ax` must be a matplotlib Axes instance or None"
        raise ValueError(msg)

    return fig, ax