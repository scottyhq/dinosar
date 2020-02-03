"""Tests for AWS Batch functionality.

For inspiration:
https://github.com/mapbox/rasterio/blob/master/cloudformation/travis.template
https://github.com/mapbox/rasterio/blob/c3b2499487d75803d1f73efb653f8698eaadb176/tests/test_env.py
"""
import dinosar.cloud.aws as daws


def test_aws_config():
    """Make sure boto3 loads credentials"""
    pass


def test_aws_batch():
    """Launch batch example"""
    pass


def test_aws_s3():
    """Make sure pushing ISCE output to S3 works"""
    pass
