# rpmusicserver
Transform a Raspberry Pi in a music server with LMS (Squeezebox), Samba, transcoder, etc.

## Steps to turn a Pi into a music server:
* download all code 
  * `wget ....`
* make scripts executable: 
  * `chmod +x ./scripts/*.sh`
* burn sd-card:
  * `sudo ./scripts/burn-image.sh`
* format usb-disk (ext4, label = usbdisk)
  * `sudo ./scripts/format-usbdisk.sh`
* hookup harddisk to the Pi
* reboot the clean system
* remote installation with install-rp script via ssh
	* `ssh pi@raspberrypi "bash -s" < ./scripts/install-rp.sh`
	* password: raspberry
* system will be rebooted automatically after installation
* test access:
  * Samba: (file explorer) smb://raspberrypi
  * LMS: (browser) http://raspberrypi:9002
  * Transmission: (browser) http://raspberrypi:9091

