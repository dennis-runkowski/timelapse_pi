#!/bin/bash

set -e

echo "###############################"
echo "Building Timelapse package...."
echo "###############################"

timestamp=$(date +%s)

tar -X ../.gitignore --exclude='../../timelapse_pi/deploy/packages' -czvf packages/build_$timestamp.tar.gz ../../timelapse_pi

echo ""
echo "#######################################"
echo "Completed"
echo "Package Name: build_$timestamp.tar.gz"
echo "#######################################"