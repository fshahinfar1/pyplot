#! /bin/bash
curdir=$(dirname $0)
install_dir=/opt/pyplot
sudo mkdir $install_dir
sudo cp -r $curdir/tools/ $install_dir/
sudo cp $curdir/pyplot /usr/bin/pyplot
