#!/bin/bash
# Release a new dinosar version
# USAGE ./make_release.sh 0.1.3
# Note that every push to GitHub automatically runs travis CI and
# Documentation will automatically be generated on Read the Docs

VERSION=$1
echo 'Creating release version $VERSION'

# remake documentation with sphinx
#cd ..
#cd docs
#sphinx-apidoc -f --no-toc -o api/ ../dinosar
#make html
#cd ..

# Create a new tagged release
git tag $VERSION ; git push --tags
git checkout tags/$VERSION -b $VERSION

# Build the package and upload to pypi
python3 setup.py sdist bdist_wheel
twine upload dist/*

# Delete the temporary branch (it's still tagged up on github
git checkout master
git branch -d $VERSION ; git push origin --delete $VERSION
