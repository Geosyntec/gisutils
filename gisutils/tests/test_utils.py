import pytest

import numpy

from gisutils import utils
from .helpers import raises


@pytest.mark.parametrize(('filename', 'expected'), [
    ('example.shp', 'example_test.shp'),
    ('example', 'example_test'),
])
def test_add_suffix_to_filename(filename, expected):
    result = utils.add_suffix_to_filename(filename, 'test')
    assert result == expected


@pytest.mark.parametrize(('column', 'value', 'expected', 'err'), [
    ('ID', 'Junk', None, None),
    ('ID', 'A1', ('A1', 'Ocean', 'A1_x', 'A1_y'), None),
    ('DS_ID', 'A1', None, ValueError),
])
def test_find_row_in_array(column, value, expected, err):
    with raises(err):
        input_array = numpy.array(
            [
                ('A1', 'Ocean', 'A1_x', 'A1_y'), ('A2', 'Ocean', 'A2_x', 'A2_y'),
                ('B1', 'A1', 'None', 'B1_y'), ('B2', 'A1', 'B2_x', 'None'),
                ('B3', 'A2', 'B3_x', 'B3_y'), ('C1', 'B2', 'C1_x', 'None'),
            ], dtype=[('ID', '<U5'), ('DS_ID', '<U5'), ('Cu', '<U5'), ('Pb', '<U5')]
        )
        result = utils.find_row_in_array(input_array, column, value)
        if expected is None:
            assert expected is result
        else:
            assert list(result) == list(expected)
