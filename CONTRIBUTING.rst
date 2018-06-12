Code Conventions
----------------

*dinosar* is setup to work with Python 3.

Code should adhere to PEP8_.

Documentation is done with Sphinx_ using Restructured Text (RST). Docstrings_ will be done using Numpy format.

Tests are mandatory for new features. We use Pytest_.


.. _PEP8: https://www.python.org/dev/peps/pep-0008/
.. _Sphinx: https://pythonhosted.org/an_example_pypi_project/
.. _Pytest: https://pytest.org/
.. _Docstrings: https://numpydoc.readthedocs.io/en/latest/format.html#docstring-standard/


Updating Verion
---------------

Version managment is done with versioneer_

To relase a new version, create a tag, checkout the tag as a local branch, push to PYPI:

    git tag 0.1.1 ; git push --tags

    git checkout tags/0.1.1 -b 0.1.1
    
    python3 setup.py sdist bdist_wheel
    
    twine upload --repository-url https://test.pypi.org/legacy/ dist/*



.. _versioneer: https://github.com/warner/python-versioneer/
