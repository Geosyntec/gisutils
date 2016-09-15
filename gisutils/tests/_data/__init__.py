from pkg_resources import resource_filename

import pytest

import gisutils


def test(*args):
    options = [resource_filename('gisutils', 'tests')]
    options.extend(list(args))
    return pytest.main(options)
