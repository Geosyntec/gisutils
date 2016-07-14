import os

try:
    import arcpy
except ImportError:
    arcpy = None

import pytest

from gisutils import mapping



@pytest.mark.skipif(arcpy is None, reason='No arcpy')
class Test_EasyMapDoc(object):
    def setup(self):
        self.mxd = resource_filename("propagator.testing.EasyMapDoc", "test.mxd")
        self.ezmd = utils.EasyMapDoc(self.mxd)

        self.knownlayer_names = ['ZOI', 'wetlands', 'ZOI_first_few', 'wetlands_first_few']
        self.knowndataframe_names = ['Main', 'Subset']
        self.add_layer_path = resource_filename("propagator.testing.EasyMapDoc", "ZOI.shp")

    def test_layers(self):
        assert hasattr(self.ezmd, 'layers')
        layers_names = [layer.name for layer in self.ezmd.layers]
        assert layers_names == self.knownlayer_names

    def test_dataframes(self):
        assert hasattr(self.ezmd, 'dataframes')
        df_names = [df.name for df in self.ezmd.dataframes]
        assert df_names == self.knowndataframe_names

    def test_findLayerByName(self):
        name = 'ZOI_first_few'
        lyr = self.ezmd.findLayerByName(name)
        assert isinstance(lyr, arcpy.mapping.Layer)
        assert lyr.name == name

    def test_add_layer_with_path(self):
        assert len(self.ezmd.layers) == 4
        self.ezmd.add_layer(self.add_layer_path)
        assert len(self.ezmd.layers) == 5

    def test_add_layer_with_layer_and_other_options(self):
        layer = arcpy.mapping.Layer(self.add_layer_path)
        assert len(self.ezmd.layers) == 4
        self.ezmd.add_layer(layer, position='bottom', df=self.ezmd.dataframes[1])
        assert len(self.ezmd.layers) == 5

    def test_bad_layer(self):
        with pytest.raises(ValueError):
            self.ezmd.add_layer(123456)

    def test_bad_position(self):
        with pytest.raises(ValueError):
            self.ezmd.add_layer(self.add_layer_path, position='junk')


@pytest.mark.skipif(arcpy is None, reason='No arcpy')
class Test_Extension(object):
    def setup(self):
        self.known_available = 'spatial'
        self.known_unavailable = 'tracking'

    @pytest.mark.skipif(True, reason="Test status: WIP")
    def test_unlicensed_extension(self):
        with pytest.raises(RuntimeError):
            with utils.Extension(self.known_unavailable):
                raise

    def test_licensed_extension(self):
        assert arcpy.CheckExtension(self.known_available) == u'Available'
        with utils.Extension(self.known_available) as ext:
            assert ext == 'CheckedOut'

        assert arcpy.CheckExtension(self.known_available) == u'Available'

    def teardown(self):
        arcpy.CheckInExtension(self.known_available)


@pytest.mark.skipif(arcpy is None, reason='No arcpy')
class Test_OverwriteState(object):
    def test_true_true(self):
        arcpy.env.overwriteOutput = True

        assert arcpy.env.overwriteOutput
        with utils.OverwriteState(True):
            assert arcpy.env.overwriteOutput

        assert arcpy.env.overwriteOutput

    def test_false_false(self):
        arcpy.env.overwriteOutput = False

        assert not arcpy.env.overwriteOutput
        with utils.OverwriteState(False):
            assert not arcpy.env.overwriteOutput

        assert not arcpy.env.overwriteOutput

    def test_true_false(self):
        arcpy.env.overwriteOutput = True

        assert arcpy.env.overwriteOutput
        with utils.OverwriteState(False):
            assert not arcpy.env.overwriteOutput

        assert arcpy.env.overwriteOutput

    def test_false_true(self):
        arcpy.env.overwriteOutput = False

        assert not arcpy.env.overwriteOutput
        with utils.OverwriteState(True):
            assert arcpy.env.overwriteOutput

        assert not arcpy.env.overwriteOutput


@pytest.mark.skipif(arcpy is None, reason='No arcpy')
class Test_WorkSpace(object):
    def setup(self):
        self.baseline = os.getcwd()
        self.new_ws = u'C:/Users'

        arcpy.env.workspace = self.baseline

    def test_workspace(self):
        assert arcpy.env.workspace == self.baseline
        with utils.WorkSpace(self.new_ws):
            assert arcpy.env.workspace == self.new_ws

        assert arcpy.env.workspace == self.baseline
