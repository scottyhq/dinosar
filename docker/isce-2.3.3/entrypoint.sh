#!/bin/bash -l

# ==== ONLY EDIT WITHIN THIS BLOCK =====

# Careful to not mount over $HOME at runtime!
echo "machine urs.earthdata.nasa.gov login $NASAUSER password $NASAPASS" > $HOME/.netrc
chmod 600 $HOME/.netrc

# ==== ONLY EDIT WITHIN THIS BLOCK =====

exec "$@"
