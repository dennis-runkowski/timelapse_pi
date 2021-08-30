# Timelapse Pi
This app allows you to create a timelapse with a raspberry pi and a pi camera! To get started you will need the follow parts:

* raspberry pi 3 (add link)
* pi camera (add link)
* case (optional but I recommend getting) (add link)

# Install
Now that you have your pi and camera you'll need to hook up the camera to the pi.
<ol>
<li>Turn the pi off</li>
<li>Pull the edges of the plastic camera port up</li>
<li>Insert the camera ribbon cable</li>
<li>Push the plastic clip down into the closed position</li>
</ol>

Next you need to setup ssh access to your pi. Here is a good tutorial: https://www.raspberrypi.org/documentation/remote-access/ssh/

This application uses python 3 and the picamera package, so we will need to install some packages on the pi. You can you the following script to setup your pi.

`./deploy/pi_setup.sh`

`sudo apt-get install python-picamera python3-picamera`

Once you have all the nesscary packages installed we can deploy the code to the pi


## Notes

onedrive install on pi
https://jarrodstech.net/how-to-raspberry-pi-onedrive-sync/

 rclone --vfs-cache-mode writes mount "onedrive":  ~/OneDrive


rclone move -v OneDrive/* onedrive:raspberry_pi_storage
