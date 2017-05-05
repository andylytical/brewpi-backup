#!/bin/bash

WWW=/var/www/html
PRGDIR=$(dirname $0)
PYTHON_PKGS=( textwrap dropbox )

#fn="$PRGDIR/bash.common"
#[[ -r $fn ]] || { echo "Cant access file '$fn'"; exit 1
#}
#source $fn

# Ensure python3
set -x
sudo apt-get update
sudo apt-get install python3 python3-pip
# Install required python packages
sudo pip3 install "${PYTHON_PKGS[@]}"
set +x

css="$PRGDIR/dygraph.2.0.0.min.css"
js="$PRGDIR/dygraph.2.0.0.min.js"
for x in css js; do
    fn_src=${!x}
    fn_tgt=$WWW/$x/
    set -x
    sudo rsync -ivptgo "$fn_src" "$fn_tgt"
    set +x
done
