# rpmusicserver
Transform a Raspberry Pi in a music server with LMS (Squeezebox), Samba, transcoder, etc.

## Steps to turn a Pi into a music server:
* Download code:
  * `wget https://github.com/markbaaijens/rpmusicserver/archive/refs/heads/master.zip -O /tmp/rpmusicserver.zip`
  * `unzip -d /tmp -o /tmp/rpmusicserver.zip`
* Burn SD-card:
  * insert SD-card into your Linux PC
  * `sudo /tmp/rpmusicserver-master/scripts/burn-image.sh`
* Format USB-drive for data (ext4, label = usbdata):
  * connect USB-drive to your Linux PC
  * `sudo /tmp/rpmusicserver-master/scripts/format-usbdisk.sh`
* First boot:
  * make sure your Pi is powered off
  * insert SD-card into your Pi
  * connect USB-drive to the Pi
  * connect the Pi to your network with a network cable 
  * power up the Pi
  * check if Pi is running: `watch nmap rpms`
    * wait until port 22 appears; exit with Ctrl-C
* Installation and configuration with install-rp script via ssh:
  * `rsync -r /tmp/rpmusicserver-master/* pi@rpms:/tmp/rpmusicserver`
	  * password = raspberry  
  * `ssh pi@rpms "sudo chmod +x /tmp/rpmusicserver/scripts/* && sudo /tmp/rpmusicserver/scripts/install-rp.sh"`
	  * password = raspberry
  * notes:
    * system will be rebooted automatically after installation
    * after reboot, password of user `pi` is changed to `rpms`
* Test access:
  * `watch nmap rpms`
    * wait until port 9002 appears; exit with Ctrl-C
  * LMS (browser): http://rpms:9002
  * Samba (file explorer): `smb://rpms`
  * API (cli): `curl rpms:5000`
* Engage:
  * copy music files to `smb://rpms/Publiek/Muziek`
  * hookup a Squeezebox player to your network
  * install a Android App like [Squeezer](https://play.google.com/store/apps/details?id=uk.org.ngo.squeezer)
  * enjoy!

## Update
Update your RPMS by SSH: 
* `ssh pi@rpms "sudo update-rpms"`

## Development: 
* To update RMPS from `development` branch instead of `master`: 
  * `ssh pi@rpms "sudo bash -c 'echo \"develop\" > /media/usbdata/config/update-branch.txt'"`
* API-documentation: `curl rpms:5000/api/getApiList`
