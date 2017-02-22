from pkg_resources import resource_filename

import gisutils


def test(*args):
    try:
        import pytest
    except ImportError as e:
        raise ImportError("`pytest` is required to run the test suite")

    options = [resource_filename('gisutils', '')]
    options.extend(list(args))
    return pytest.main(options)
