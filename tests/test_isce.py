import dinosar.isce as dice
# from dinosar.archive import asf
import os.path


def test_read_yml_template():
    """Read a yaml file into python ordered dictionary."""
    inputDict = dice.read_yaml_template('./data/topsApp-template-uniongap.yml')

    assert isinstance(inputDict, dict)
    assert inputDict['topsinsar']['azimuthlooks'] == 7


def test_write_topsApp_xml():
    """Make sure directory is created with necessary and valid files."""
    testDict = {'topsinsar': {'azimuthlooks': 7,
                              'filterstrength': 0.5,
                              'master': {'safe': 's1a.zip'},
                              'slave': {'safe': 's1b.zip'}
                              }
                }
    xml = dice.dict2xml(testDict)
    dice.write_xml(xml)

    assert os.path.exists('topsApp.xml')


def test_create_cmaps():
    """Create .cpt files from matplotlib colormaps."""
    dice.make_cmap('phsig.cor.geo.vrt')
    assert os.path.exists('coherence-cog.cpt')

    dice.make_cmap('filt_topophase.unw.geo.vrt')
    assert os.path.exists('unwrapped-phase-cog.cpt')

    dice.make_cmap()
    assert os.path.exists('amplitude-cog.cpt')


'''
def test_isce2cog(url):
    """Convert isce geocoded output to cloud optimized geotiff (COG)."""
    dice.make_cog()
    # dice.make_rgb()
    # dice.make_thumbnails()
    # curl -s "http://cog-validate.radiant.earth/api/validate?url=http://path/to/my.tif"
    assert os.path.exists('coherence-cog.tif')
'''
