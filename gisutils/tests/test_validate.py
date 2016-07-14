import numpy
from matplotlib import pyplot

import pytest
import numpy.testing as nptest

from gisutils import validate


@pytest.mark.parametrize(('value', 'expected'), [
    (1, numpy.array([1])),
    (1., numpy.array([1.])),
    (None, numpy.array([None])),
    ('test', numpy.array(['test'])),
    ([1, 2, 3], numpy.array([1, 2, 3])),
    (numpy.array([1, 2, 3]), numpy.array([1, 2, 3])),
    (numpy.array([[1, 2, 3], [4, 5, 6]]), numpy.array([1, 2, 3, 4, 5, 6])),

])
def test_is_vector(value, expected):
    result = validate.is_vector(value)
    nptest.assert_array_equal(result, expected)


def test_mpl_axes_invalid():
    with pytest.raises(ValueError):
        validate.mpl_axes('junk')


def test_mpl_axes_with_ax():
    fig, ax = pyplot.subplots()
    fig1, ax1 = validate.mpl_axes(ax)
    assert isinstance(ax1, pyplot.Axes)
    assert isinstance(fig1, pyplot.Figure)
    assert ax1 is ax
    assert fig1 is fig


def test_mpl_axes_with_None():
    fig1, ax1 = validate.mpl_axes(None)
    assert isinstance(ax1, pyplot.Axes)
    assert isinstance(fig1, pyplot.Figure)
