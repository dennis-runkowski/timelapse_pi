#!/bin/bash

set -e

ssh_config=$1

if [ -z "$ssh_config" ]
then
	echo "Please add your ssh config i.e ./build SSH_CONFIG_NAME"
	exit 1
else
	echo ""
	echo "Deploying to $ssh_config"
	echo ""
fi

./build.sh

./deploy.sh $1

ssh -t $1 'cd /tmp/package && ./install.sh'