#!/usr/bin/env bash

pushd $(dirname -- "$0")/../external/LuaJIT/src
system_name=$1
install_path=$2

mkdir $install_path/include/
mkdir $install_path/lib/

cp *.h *.hpp $install_path/include/

# TODO: use $system_name!!!
cp lua51.lib $install_path/lib/
popd
