#!/bin/bash

set -x

(
WWW=/var/www/html
PRGDIR=$(dirname $0)
PYTHON_PKGS=( dropbox )


# Ensure python3
sudo apt-get update
sudo apt-get -y install python3 python3-pip
# Install required python packages
sudo pip3 install "${PYTHON_PKGS[@]}"

css="$PRGDIR/dygraph.2.0.0.min.css"
js="$PRGDIR/dygraph.2.0.0.min.js"
for x in css js; do
    fn_src=${!x}
    fn_tgt=$WWW/$x/
    sudo rsync -ivptgo "$fn_src" "$fn_tgt"
done

# Enable user 'pi' to write to html/data area
sudo usermod -a -G www-data pi
) | tee "$(dirname $0)/install.log"
