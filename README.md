# rpmusicserver
Transform a Raspberry Pi in a music server with LMS (Squeezebox), Samba, transcoder, etc.

## Steps to turn a Pi into a music server:
* Download all code 
  * `wget https://github.com/markbaaijens/rpmusicserver/archive/refs/heads/master.zip -O rpmusicserver.zip`
  * `unzip rpmusicserver.zip`
* Burn sd-card:
  * `sudo rpmusicserver-master/scripts/burn-image.sh`
* Format usb-disk for data (ext4, label = usbdata)
  * `sudo rpmusicserver-master/scripts/format-usbdisk.sh`
* Hookup harddisk to the Pi
* Reboot the clean system
* Check if Pi is running
  * `ping raspberrypi`
* Installation and configuration with install-rp script via ssh
  * `rsync -r rpmusicserver-master/* pi@raspberrypi:/tmp/rpmusicserver`
  * `ssh pi@raspberrypi "sudo chmod +x /tmp/rpmusicserver/scripts/* && sudo /tmp/rpmusicserver/scripts/install-rp.sh"`
	* password = raspberry
* System will be rebooted automatically after installation
* Test access:
  * `watch nmap raspberrypi`
  * Samba: (file explorer) `smb://raspberrypi`
  * LMS: (browser) http://raspberrypi:9002
  * (Transmission: (browser) http://raspberrypi:9091)
* Engage
  * copy music files to smb://raspberrypi/Publiek/Muziek
  * hookup a Squeezebox player to your network
  * enjoy!
