# RP Music Server
Transforms a Raspberry Pi in a music server with LMS (Logitech Media Server/Squeezebox), Samba, Transmission, Syncthing, transcoder, etc.

## System requirements
* [minimum] Raspberry Pi 2 (B or B+), 1 GB
* [recommended] Raspberry Pi 4 B, 4 GB

## Installation of RPMS on a Pi
* Install package(s) on your Linux PC:
  * `sudo apt-get install nmap`
    * enter your (personal) password of your PC  
* Download code:
  * `wget https://github.com/markbaaijens/rpmusicserver/archive/refs/heads/master.zip -O /tmp/rpmusicserver.zip`
  * `unzip -d /tmp -o /tmp/rpmusicserver.zip`
* Burn SD-card:
  * insert SD-card into your Linux PC
  * `sudo /tmp/rpmusicserver-master/scripts/burn-image.sh`
    * enter your (personal) password of your PC
* Format USB-drive for data:
  * connect USB-drive to your Linux PC
  * `sudo /tmp/rpmusicserver-master/scripts/format-usbdisk.sh`
    * enter your (personal) password of your PC
  * follow the instructions to format as a DATA-disk    
* First boot:
  * make sure your Pi is powered off
  * insert SD-card into your Pi
  * connect USB-drive to the Pi
  * connect the Pi to your network with a network cable 
  * power up the Pi
  * check if Pi is running: 
    * `watch nmap rpms`
    * wait until port 22 appears; exit with Ctrl-C
* Installation and configuration:
  * `rsync -r /tmp/rpmusicserver-master/* pi@rpms:/tmp/rpmusicserver`
	  * password = raspberry  
  * `ssh pi@rpms "sudo chmod +x /tmp/rpmusicserver/scripts/* && sudo /tmp/rpmusicserver/scripts/install-rp.sh"`
	  * password = raspberry
  * notes:
    * system will be rebooted automatically after installation
    * after reboot, password of user `pi` is changed to `rpms`
* Test access:
  * watch services to become active:
    * `watch nmap rpms`
      * wait until port 9002 appears; exit with Ctrl-C
    * [rpms/services](http://rpms:80/services)
      * wait until port 9002 is active
  * RPMS (browser): [rpms](http://rpms:80)
  * LMS (browser): [rpms:9002](http://rpms:9002)
  * Transmission (browser): [rpms:9091](http://rpms:9091)
  * Samba (file explorer): `smb://rpms`
  * Syncthing: [rpms:8384](http://rpms:8384)
  * API: 
    * `curl rpms:5000`
  * SSH: 
    * `ssh pi@rpms`
    * password: rpms
* Engage:
  * copy music files to `smb://rpms/Publiek/Muziek`
  * hookup a Squeezebox player to your network
  * install a Android App like [Squeezer](https://play.google.com/store/apps/details?id=uk.org.ngo.squeezer)
  * enjoy!

## Troubleshooting
### *Pi/rpms cannot be reached on the network*
Sometimes the pi is not visible in the network, either by hostname `rpms` or even by ip-address.

* if rpms cannot be found, first try pinging for rpms:
  * `ping rpms`
* if there is no response from the ping-command, check if pi is running and properly connected to the network (watch network-leds on the pi)
* if there is no response from the ping-command, try:
  * `nmap 192.168.x.*`
  * fill for x your personal subnet-number; use `hostname -I` to retrieve that info
* try to ping by ip-address (if hostname `rpms` is not mentioned by nmap)
  * ping 192.168.x.y
* for most network-problems (no hostname shown for pi, multiple ip-addresses for hostname, not able to ping on hostname, etc.):
  * reboot router
* if hostname `rpms` is not found (after reboot router):
  * reboot pi (best done by rpms web-interface) 

### *Pi/rpms can only reached by ip-address*
On some local networks, there might be a problem present that the hostname of all connected devices, including RPMS cannot be resolved. In practice, `ping rpms` does not return anything. So any command directly targeted at RPMS such as `ssh pi@rpms` does not work. This is a problem within the router/network, the origin of this problem is unknown to date.

The good news however is that a device is *always* accesible by ip-address. So once you know the ip-address of your RPMS-instance, by executing `nmap 192.168.x.*` (x is the subnet, normally 1 or 2), you can install, configure and use RPMS.

All you have to do is the following: in any command in the section *Installation of RPMS on a Pi* (and following sections), replace RPMS with the discovered ip-address.

So for example, if the ip-address of RPMS is 192.68.1.20: `ping rpms` will become `ping 192.68.1.20`. And `ssh pi@rpms` will become `ssh pi@192.68.1.20`. In your browser, LMS `rpms:9002` wil become `192.68.1.20:9002` Etc. 

Note that the ip-address might change over time b/c RPMS does not use a fixed address, but instead depends on the router which determines the address. In that case, point to the new address.

### *Reconnect players after LMS migration*
When migrating from an existing LMS-server or upgraded your Pi-hardware, you have to reconfigure all players to point to the new LMS-server (even if LMS has the same name). This is especially true for Squeezebox-hardware like Squeezebox Classic, Duet, Touch, Radio, Boom or Transporter. Note: clients with piCorePlayer will autodetect the new LMS-server.

Reconfiguring is best done:
* by the Squeezer-app (per player, disconnect server and reconnect)
* (or) by the Squeezebox Controller (per player, change 'Music Collection')
* (or) on the Squeezebox-device itself (all except Duet which has no physical interface)

## Update
Update your RPMS-server: 
* [rpms/tasks](http://rpms:80/tasks)
* click Update

## Development

### Update from another git branch
RPMS can be updated from a github branch, where the rpms-code is stored. The update depends on version-numbering in the file `revision.json` (locally stored on rpms) on one hand and on `revision.json` in the github-repo in the other hand. 

By default, the update-mechanism looks at the `master` branch on github. However, it is possible to override the `master` branch version, by setting the desired branch version to a different value. In most cases this is the `develop` branch. As a result, an indicator VersionOverride pops up in the web-interface.

Note that once VersionOverride is active, CurrentVersion and AvailableVersion do not play a role anymore.

To switch version from `master` branch to e.g. `develop` branch:
* `ssh pi@rpms "sudo bash -c 'echo \"develop\" > /media/usbdata/rpms/config/update-branch.txt'"`

Returning to the `master` branch version simply delete the `/media/usbdata/rpms/config/update-branch.txt` text file.

### Build development version with separate hostname
The `rpmsdev` hostname is used in this build
* `cd <source-folder of rpmusicserver>`
* `sudo scripts/burn-image.sh`
  * choose type `d = development`
* `rsync -r ./* pi@rpmsdev:/tmp/rpmusicserver`
  * password = raspberry  
* `ssh pi@rpmsdev "sudo chmod +x /tmp/rpmusicserver/scripts/* && sudo /tmp/rpmusicserver/scripts/install-rp.sh"`  
  * password = raspberry 
* after reboot, password is changed to `rpms`
* from now on, you can reach the development-server on `rpmsdev`
* in case hostnames `rpms` and `rpmsdev` get mixed up, flush DNS:
  * `sudo systemd-resolve --flush-caches`

### List of API requests 
  * `curl rpms:5000/api/GetApiList`
  * [rpms:5000/api/GetApiList](http://rpms:5000/api/GetApiList)

## Transcoder
For transcoding your lossless files (flac) into lossy ones (ogg or mp3), take the following steps:
* in your file explorer
  * create a folder `flac` under `smb://rpms/Publiek/Muziek`
  * move your flac-files into that folder `flac`
* in [LMS](http://rpms:9002) Server Settings, point music-folder to this location:
  * `/music/flac`
* change [setting](http://rpms/transcoder/edit) `SourceFolder`
  * point to `/media/usbdata/user/Publiek/Muziek/flac`
  * click  Save
* for transcoding to ogg
  * in your file explorer
    * create a folder `ogg` under `smb://rpms/Publiek/Muziek`
  * change [setting](http://rpms/transcoder/edit) `OggFolder`
    * point to `/media/usbdata/user/Publiek/Muziek/ogg`
    * click Save
* for transcoding to mp3
  * in your file explorer
    * create a folder `mp3`under `smb://rpms/Publiek/Muziek`
  * change [setting](http://rpms/transcoder/edit) `Mp3Folder`
    * point to `/media/usbdata/user/Publiek/Muziek/mp3`
    * click Save
* from now on, every hour at 20 minutes, file transcoding will take place and lossy-files will automagically appear in the given lossy-folder!
* see transcoder-progress
  * [rpms/logs/transcoder/20](http://rpms/logs/transcoder/20)
  * `curl rpms:5000/api/GetTranscoderLog/20`

### Notes
* Transcoding will be done by these default quality-levels: ogg = 1, mp3 = 128. Optionally, you can change these defaults:
  * for example, change [setting](http://rpms/transcoder/edit) `OggQuality` to 3 (value = 1, 2, 3, 4, or 5):
  * for example, change [setting](http://rpms/transcoder/edit) `Mp3Bitrate` to 256 (value = 128, 256 or 384):
* Trancoding simultaneously to ogg AND mp3 is possible; just set both `OggFolder` and `Mp3Folder`

## Backup
You can make a backup of all the data contained in your RPMS-server. This backup will be done to a dedicated backup-disk, connected to the Pi it self, a so called server-based backup.

* format a disk dedicated for RPMS-backups (one-time only):
  * connect your (empty) backup-disk to your PC
  * `wget https://github.com/markbaaijens/rpmusicserver/raw/master/scripts/format-usbdisk.sh -O /tmp/format-usbdisk.sh && chmod +x /tmp/format-usbdisk.sh && sudo /tmp/format-usbdisk.sh`
    * enter your (personal) password of the client-machine
  * follow the instructions to format as a BACKUP-disk
* engage the backup:
  * connect your backup-disk to the Pi
  * start the backup
    * [rpms/tasks](http://rpms/tasks
    * click BackupServer
  * watch overall progress
    * [rpms/logs/backup/20](http://rpms/logs/backup/20)
    * refresh until log states: 'Backup ended'
  * watch detailed progress
    * [rpms/logs/backup-details/20](http://rpms/logs/backup-details/20)
  * see full backup-log
    * [rpms/logs/backup-details/0](http://rpms/logs/backup-details/0)
  * disconnect backup-disk

### Off-line backup-data viewing
Backup-disk is formatted as ext4; for off-line viewing on your own PC, this format is natively supported on Linux, so it is plug-and-play. Windows however requires additional drivers for viewing ext-drives. And worse, MacOS does NOT support ext4 at all! (despite extX being open-source/open-standard).

## Disaster-recovery
Disaster can come from anywhere: a broken Pi (very unlikely), a corrupt SD-card or a data-disk which get broken. In each case, the solution within RPMS is very simple
* *broken Pi* => just obtain a new Pi which meets the system requirements (see above), swap the SD-card and boot up the Pi (possible need to reconnect player, see Troubleshooting-section)
* *corrupt SD-card* => re-burn en re-install RPMS (see above for instructions) on the same card (if the hardware is damaged, obtain a new card); then you can reboot the Pi and you are ready to go (possible need to reconnect player, see Troubleshooting-section)
* *data-disk crash* =>  b/c the backup-disk is an exact copy aka mirror of the data-disk and even of the same disk-type (ext4), you can simply swap them once the data-disk has been crashed. Just rename the label of the backup-disk from `usbbackup` to `usbdata` with your favourite disk-tool (Disks, gparted, etc.), connect the disk to the Pi and boot up. The backup-disk has been automagically changed into a data-disk by now and you can go on from the last backup that you made. Remember to make a backup to a new backup-disk immediately!
