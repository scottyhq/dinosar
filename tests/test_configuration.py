import os.path


def test_netrc():
    """Check ~/.netrc file exists in order to download from ASF."""
    netrcPath = os.path.join(os.path.expanduser('~'), '.netrc')

    assert os.path.exists(netrcPath)


def test_awscredentials():
    """Check ~/.aws/credentials exists in order to download run AWS Batch."""
    awsPath = os.path.join(os.path.expanduser('~'), '.aws', 'credentials')

    assert os.path.exists(awsPath)
