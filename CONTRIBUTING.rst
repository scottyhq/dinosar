Code Conventions
----------------

*dinosar* is designed to work with Python >3.6

Code should adhere to PEP8_.

Documentation is done with Sphinx_ using Restructured Text (RST). Docstrings_ will be done using Numpy format.

Tests are mandatory for new features. We use Pytest_.


.. _PEP8: https://www.python.org/dev/peps/pep-0008/
.. _Sphinx: https://pythonhosted.org/an_example_pypi_project/
.. _Pytest: https://pytest.org/
.. _Docstrings: https://numpydoc.readthedocs.io/en/latest/format.html#docstring-standard/


Installing Development Version
------------------------------
Install from github with conda and pip::

  git clone https://github.com/scottyhq/dinosar.git
  cd dinosar
  conda env create -f ci/requirements-py37.yml
  pip install -e .


Preview documentation
---------------------
If you edit documentation (including docstrings in code), preview locally with sphinx::

  cd docs
  sphinx-apidoc -f -o source ../dinosar
  make html
  open _build/html/index.html


Updating Version
----------------

Version management is done with versioneer_

To release a new version run `./make_release.sh 0.1.1`

.. _versioneer: https://github.com/warner/python-versioneer/
