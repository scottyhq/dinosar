import os.path
import pytest

import argparse
import configparser


def dict2xml(dictionary, root='topsApp', topcomp='topsinsar'):
    """Convert simple dictionary to XML for ISCE

    """
    def add_property(property, value):
        xml = f"        <property name={property}>{value}</property>\n"
        return xml

    def add_component(name, properties):
        xml = f"    <component name={name}>\n"
        for prop, val in properties.items():
            xml += add_property(prop, val)
        xml += f"    </component>\n"
        return xml

    xml = f'<{root}>\n   <{topcomp}>\n'
    for key, val in dictionary.items():
        if isinstance(val, dict):
            xml += add_component(key, val)
        else:
            xml += add_property(key, val)

    xml += f'    <{topcomp}>\n<{root}>\n'
    return xml


def load_topsApp_defaults():
    """Load defaults from python configuration file."""
    testDict = {'azimuthlooks': '7',
                'rangelooks': '19',
                'swaths': [1, 2, 3],
                'master': {
                    'safe': 'test.zip'},
                'slave':
                    {'safe': 'another.zip'},
                }
    config = configparser.ConfigParser()
    config.read('../dinosar/isce/topsApp-defaults.cfg')
    defaults = dict(config['topsinsar'])
    xml = dict2xml(defaults, 'topsinsar')
    # result.update({k: v for k, v in args.items() if v is not None})
    assert


@pytest.mark.skip(reason="Fails on travis")
def test_netrc():
    """Check ~/.netrc file exists in order to download from ASF."""
    netrcPath = os.path.join(os.path.expanduser('~'), '.netrc')

    assert os.path.exists(netrcPath)


@pytest.mark.skip(reason="Fails on travis")
def test_awscredentials():
    """Check ~/.aws/credentials exists in order to download run AWS Batch."""
    awsPath = os.path.join(os.path.expanduser('~'), '.aws', 'credentials')

    assert os.path.exists(awsPath)
