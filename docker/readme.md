# Local build instructions

These images are intended to be as small as possible. Installing on top of Ubuntu 18.04 and required python packages all installed through apt. (Python 3.6)

isce-2.3.2: basic config (758MB)
isce-2.3.2-mdx: MDX / X11 graphics support (798MB)
isce-2.3.2-gpu: NVIDIA GPU support (783MB)
* awscli = 1.18.25

Alternatively, you can now install isce2 via conda-forge. This enables much more up-to-date versions, but generally results in a much larger image.

isce-2.3.2-conda: isce2 and other packages from conda-forge (1.9GB)


To build:
```
cd isce-2.3.2
docker build . -t dinosar/isce2:2.3.2
```
