import nose.tools as nt

from propagator import validate


class Test_non_empty_list(object):
    def test_baseline(self):
        x = [1, 2, 3]
        nt.assert_list_equal(validate.non_empty_list(x), x)

    def test_scalar(self):
        x = 1
        nt.assert_list_equal(validate.non_empty_list(x), [x])

    @nt.raises(ValueError)
    def test_None_raises(self):
        validate.non_empty_list(None)

    def test_None_creates(self):
        nt.assert_list_equal(validate.non_empty_list(None, on_fail='create'), [])

    @nt.raises(ValueError)
    def test_empty_list_raises(self):
        validate.non_empty_list([])

    def test_empty_creates(self):
        nt.assert_list_equal(validate.non_empty_list([], on_fail='create'), [])
