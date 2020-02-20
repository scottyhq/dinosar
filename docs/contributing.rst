Contributing
============

Contributing to dinosar is welcome and encouraged! Please collaborate directly on GitHub: https://github.com/scottyhq/dinosar

Code conventions
----------------

*dinosar* is designed to work with Python >3.6. As an open source project we encourage contributions. The information below will help get started, but for more information related to standard github workflows read through the excellent step-by-step contribution guide for the xarray project (http://xarray.pydata.org/en/stable/contributing.html).

Code formatting is done with Black_. Documentation uses Sphinx_ with Restructured Text format (RST). Docstrings_ use Numpy format. Tests are mandatory for new features and run via Pytest_.

.. _Black: https://black.readthedocs.io/en/stable/
.. _Sphinx: https://pythonhosted.org/an_example_pypi_project/
.. _Pytest: https://pytest.org/
.. _Docstrings: https://numpydoc.readthedocs.io/en/latest/format.html#docstring-standard/


Installing development version
------------------------------
Dependency management and Python package creation is done with Poetry_, and pre-commit_ runs formatting checks automatically with each git commit. To setup a local development environment, first create a virtual environment with _Conda. We also use conda to install geospatial libraries from conda-forge because they often have complicated dependencies on legacy system libraries::

  git clone https://github.com/scottyhq/dinosar.git
  cd dinosar
  conda env create -f environment-poetry.yml
  conda activate environment-poetry.yml
  poetry install
  poetry run pre-commit install

.. _pre-commit: https://pre-commit.com
.. _Poetry: https://github.com/python-poetry/poetry
.. _Conda: https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html


Run tests
---------
Run tests locally with pre-commit and pytest::

  poetry run pre-commit run --all-files
  poetry run pytest --cov=dinosar --cov-report=xml
  poetry export --without-hashes -f requirements.txt > requirements.txt

Preview documentation
---------------------
If you edit documentation (including docstrings in code), preview locally with sphinx::

  cd docs
  make api
  make html
  open _build/html/index.html


Releasing new versions
----------------------
This repository is setup with GitHub Actions CI/CD, so pushing a tag to the master branch uploads a new release to PyPi::

  VERSION=v0.1.3
  git tag $VERSION ; git push --tags
