#! /bin/bash
curdir=$(dirname "$0")
install_dir="/opt/pyplot"
sudo mkdir -p "$install_dir"
sudo cp -r "$curdir/tools/" "$install_dir/"

if [ "$OSTYPE" = "linux-gnu" ]; then
	# NOTE: on Mac, I'm not installing this here, but manually placing it in a
	# local bin folder
	sudo cp "$curdir"/pyplot /usr/bin/pyplot
fi
