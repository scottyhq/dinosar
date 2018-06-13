import versioneer
import os
from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))

# Dependencies.
with open('requirements.txt') as f:
    requirements = f.readlines()
install_requires = [t.strip() for t in requirements]

with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='dinosar',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description='SAR processing on the Cloud',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/scottyhq/dinosar',
    author='Scott Henderson',
    author_email='scottyh@uw.edu',
    maintainer='Scott Henderson',
    maintainer_email='scottyh@uw.edu',
    python_requires='>=3.6',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering'
    ],
    keywords=['SAR', 'Cloud', 'Batch', 'AWS'],
    packages=find_packages(),
    install_requires=install_requires,
    scripts=['bin/get_inventory_asf.py'],
)
