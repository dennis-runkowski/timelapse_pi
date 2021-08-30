#!/bin/bash
set -e

timestamp=$(date +%s)
echo "###############################"
echo " Backing up /opt/timelapse_pi"
echo "###############################"
# Ensure permissions again for safety
sudo chown -R pi:pi /opt/
sudo chown -R pi:pi /opt/timelapse_pi/
sudo chown -R pi:pi /home/timelapse_pi/

# Backup code
mkdir -p /opt/timelapse_pi/
mkdir -p /home/timelapse_pi/backups
tar -zcvf /home/timelapse_pi/backups/backup_$timestamp.tar.gz /opt/timelapse_pi

# Clean up old backups
find /home/timelapse_pi/backup* -mtime +15 -exec rm {} \;

echo "###############################"
echo " Installing timelapse...."
echo "###############################"

package_name=$(ls /tmp/package/build* -Art | tail -n 1)
cd /tmp/package && tar -zxvf $package_name
cd /tmp/package && rsync -r timelapse_pi/* /opt/timelapse_pi/
sudo rm -rf /tmp/package

# Ensure permissions again for safety
sudo chown -R pi:pi /opt/timelapse_pi/

echo "###############################"
echo " Installing Python Packages"
echo "###############################"

# source virtualenv
source /opt/timelapse_virtualenv/bin/activate

cd /opt/timelapse_pi
pip install -r requirements.txt
python setup.py develop

echo "###################################"
echo " Completed!"
echo " Run /opt/timelapse_pi/app/run.sh to start the app"
echo "###################################"
echo ""
