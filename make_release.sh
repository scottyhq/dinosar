#!/bin/bash
# Release a new dinosar version

VERSION=$1
echo 'Creating release version $VERSION'

# remake documentation with sphinx
cd docs
make html
cd ..

# Create a new tagged release
git tag $VERSION ; git push --tags
git checkout tags/$VERSION -b $VERSION

# Build the package and upload to pypi
python3 setup.py sdist bdist_wheel
twine upload dist/*

# Delete the temporary branch (it's still tagged up on github
git checkout master
git branch -d $VERSION ; git push origin --delete $VERSION
