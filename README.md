# RP Music Server
Transform a Raspberry Pi into a streaming/-file-server for your music with LMS (Lyrion/Logitech Media Server/Squeezebox), Samba, Transmission, Syncthing, transcoder, etc. in a few simple steps.

[System requirements](https://github.com/markbaaijens/rpmusicserver#system-requirements)<br/> 
[Check your network if local DNS works](https://github.com/markbaaijens/rpmusicserver#check-your-network-if-local-dns-works)<br/> 
[Installation of RPMS on a Pi](https://github.com/markbaaijens/rpmusicserver#installation-of-rpms-on-a-pi)<br/> 
[Troubleshooting](https://github.com/markbaaijens/rpmusicserver#troubleshooting)<br/> 
[Folder mapping](https://github.com/markbaaijens/rpmusicserver#folder-mapping)<br/> 
[Update RPMS](https://github.com/markbaaijens/rpmusicserver#update-rpms)<br/> 
[Transcoder](https://github.com/markbaaijens/rpmusicserver#transcoder)<br/> 
[Backup](https://github.com/markbaaijens/rpmusicserver#backup)<br/> 
[Disaster Recovery](https://github.com/markbaaijens/rpmusicserver#disaster-recovery)<br/> 
[Development](https://github.com/markbaaijens/rpmusicserver#development)<br/> 
[Migrating to 1.0](https://github.com/markbaaijens/rpmusicserver#migrating-to-10)<br/> 

## System requirements
* Raspberry Pi: 
  * minimum: Pi 3 (B or B+), 1 GB; recommended: Pi 4 B, 4 GB
* SD Card: 
  * minimum: 16 GB; recommended: 32 GB
* Linux PC: 
  * for installation purposes, a Linux PC is required
  * once installed, any OS will do, be it Windows, Linux or MacOS

## Check your network if local DNS works
To detect if your network supports local DNS, execute the following command in a terminal:
* `nslookup $(hostname) $(ip route | grep default | awk '{print $3}') | grep "Can't find"`

Check for output:
* _no output_, it is all good and you can proceed installing RPMS on your Pi.
* _output produced_, it means that your local DNS is not working. No worries, this problem can be solved, just follow the steps in the troubleshooting-section below, or more specific [Pi/rpms can only reached by ip-address](https://github.com/markbaaijens/rpmusicserver#pirpms-can-only-reached-by-ip-address)

## Installation of RPMS on a Pi
Installing RPMS on your Pi can be done with a few simple steps, described below. But first, you should test your network if local DNS works.

### Steps to install RPMS on your Pi
* Install package(s) on your Linux PC:
  * `sudo apt-get install nmap`
    * enter your (personal) password of your PC  
* Download code:
  * `wget https://github.com/markbaaijens/rpmusicserver/archive/refs/heads/master.zip -O /tmp/rpmusicserver.zip && unzip -d /tmp -o /tmp/rpmusicserver.zip`
* Burn SD-card:
  * insert SD-card into your Linux PC
  * `sudo /tmp/rpmusicserver-master/scripts/burn-image.sh`
    * enter your (personal) password of your PC
    * Select a disk: choose the inserted SD-card
    * Select a type: choose P for Production
    * Do you want to continue burning on [chosen device]: type 'yes'        
* Format USB-drive for data:
  * connect USB-drive to your Linux PC
  * `sudo /tmp/rpmusicserver-master/scripts/format-usbdisk.sh`
    * enter your (personal) password of your PC
    * Select a disk: select the inserted USB-disk
    * Select a format-type: choose D for data-disk
    * Do you want to continue formatting [chosen device] as 'usbbackup': type 'yes'  
* First boot:
  * make sure your Pi is powered off
  * insert SD-card into your Pi
  * connect USB-drive to the Pi
  * connect the Pi to your network with a network cable 
  * power up the Pi
  * check if Pi is running: 
    * `watch nmap rpms`
    * wait until port 22 appears; exit with Ctrl-C
    * _if the Pi does not appear in the network, checkout the Troubleshooting-section below_
* Installation:
  * `rsync -r /tmp/rpmusicserver-master/* pi@rpms:/tmp/rpmusicserver`
	  * password = raspberry  
  * `ssh pi@rpms "sudo chmod +x /tmp/rpmusicserver/scripts/* && sudo /tmp/rpmusicserver/scripts/install-rp.sh"`
	  * password = raspberry
  * notes:
    * after installation, password of user `pi` is changed to `rpms`
* Test access:
  * watch services to become active:
    * `watch nmap rpms`
    * wait until port 9002 appears; exit with Ctrl-C
  * RPMS (browser): http://rpms
  * LMS (browser): http://rpms:9002
  * Transmission (browser): http://rpms:9091
  * Samba (file explorer): 
    * `smb://rpms`
  * Syncthing: http://rpms:8384
  * API: 
    * `curl rpms:5000`
  * SSH: 
    * `ssh pi@rpms`
    * password: rpms
* Engage:
  * copy music files to `smb://rpms/<music folder>`
  * hookup a Squeezebox player to your network
  * install a Android App like [Squeezer](https://play.google.com/store/apps/details?id=uk.org.ngo.squeezer)
  * enjoy!

## Folder mapping
For several services within RPMS, container-technology docker is used. Within docker, there is no direct link to the file-system, but this is achieved through a virtual folder which is set during installation. Normally, an end-user does not have to know about these virtual folders, but there are a few exceptions primarily around LMS and SyncThing. These specific case have to be documented.

Mapping from virtual folder to fysical folders:
* LMS: /music => rpms://user/[music]
* SyncThing: => /data => rpms://user

So when working the inside of the docker-infrastructure, either LMS or SyncThing, refer to the virtual folders.

## Troubleshooting
### *Pi/rpms cannot be reached on the network*
Sometimes the pi is not visible in the network, either by hostname `rpms` or even by ip-address.

* if rpms cannot be found, first try pinging for rpms:
  * `ping rpms`
* if there is no response from the ping-command: 
  * check if pi is running and properly connected to the network (watch network-leds on the pi)
* if there is no response from the ping-command, try:
  * `nmap $(echo "$(hostname -I | cut -d"." -f1-3).1")/24 -p 22 --open`
  * find the device with open port 22, that might be the Pi
* try to ping RPMS by ip-address
  * ping 192.168.x.y
  * if the server responds, proceed with _Pi/rpms can only reached by ip-address_
  
If everything fails (no hostname shown for pi, multiple ip-addresses for hostname, not able to ping on hostname, etc.), try:
* reboot router
* reboot pi (best done by rpms web-interface) 
* connect a keyboard and display to the pi to troubleshoot the issue directly from the device

### *Pi/rpms can only reached by ip-address*
On some local networks, there might be a problem present that the hostname of all connected devices, including RPMS cannot be resolved. In practice, `ping rpms` does not return anything. So any command directly targeted at RPMS such as `ssh pi@rpms` does not work. This is a problem within the router/network, the origin of this problem is unknown to date.

The good news however is that a device is *always* accesible by ip-address. So once you know the ip-address of your RPMS-instance, you can install, configure and use RPMS. All you have to do is the following: in any command in the section *Installation of RPMS on a Pi* (and following sections), replace RPMS with the discovered ip-address.

So for example, if the ip-address of RPMS is 192.68.1.20: `ping rpms` will become `ping 192.68.1.20`. And `ssh pi@rpms` will become `ssh pi@192.68.1.20`. In your browser, LMS `rpms:9002` wil become `192.68.1.20:9002` Etc. 

Note that the ip-address might change over time b/c RPMS does not use a fixed address, but instead depends on the router which determines the address. In that case, point to the new address.

### *Reconnect players after LMS migration*
When migrating from an existing LMS-server or upgraded your Pi-hardware, you have to reconfigure all players to point to the new LMS-server (even if LMS has the same name). This is especially true for Squeezebox-hardware like Squeezebox Classic, Duet, Touch, Radio, Boom or Transporter. Note: clients with piCorePlayer will autodetect the new LMS-server.

Reconfiguring is best done:
* by the Squeezer-app (per player, disconnect server and reconnect)
* (or) by the Squeezebox Controller (per player, change 'Music Collection')
* (or) on the Squeezebox-device itself (all except Duet which has no physical interface)

## Update RPMS
Update your RPMS-server by the web-interface: 
* Under Home, Version, click on the Update-button

You can also opt to update through ssh on rpms: 
* `ssh pi@rpms`
* `sudo update-rpms`

Note. Update is disabled when there is no newer version found.

## Transcoder
Within RPMS, there is a trancoder built in, for transcoding your lossless music files (flac) into lossy ones (ogg or mp3). By default, the transcoder is not active, it must be configured to become active.

### Enabling transcoder
For getting trancoding to work, take the following steps: 
* in your file explorer
  * create a folder `flac` under `smb://<music folder>`
  * move your flac-files into that folder `flac`
* in LMS Server Settings, modify music-folder:
  * from  `/music`
  * to `/music/flac`
* in the web-interface, under Transcoder, Edit, change setting `Source Folder`
  * point to `flac`
* for transcoding to ogg
  * in your file explorer, create a folder `ogg` under `smb://rpms/<music folder>`
  * in the web-interface, under Transcoder, Edit, change setting `Ogg Folder`
    * point to `ogg`
* for transcoding to mp3
  * in your file explorer, create a folder `mp3`under `smb://rpms/<music folder>`
  * in the web-interface, under Transcoder, Edit, change setting `Mp3 Folder`
    * point to `mp3`

From now on, file transcoding will take place and lossy-files will automagically appear in the given lossy-folder without any interaction.

In the Transcoder-page, You can also click on the Transcode-button, to start an immediate transcoding session, for if you do want to wait for the automatic session to kick in. Note that this button is diabled if transcoding is not configured.

### Notes
* some default quality-levels are used for transcoding: ogg = 1, mp3 = 128; optionally, you can change these defaults through the web-interface under Transcoder
* you can simultaneously transcode to ogg AND mp3; just set both `Ogg Folder` and `Mp3 Folder`

## Backup
You can make a backup of all the data contained in your RPMS-server. You have the choice for a full, server-based backup. Or a remote backup, where your backup contains basically the data/user-part of RPMS. A proper backup is the basis for [disaster recovery](https://github.com/markbaaijens/rpmusicserver#disaster-recovery).

### Server-based backup 
The advantage of the server-based (local) backup is that the resulting backup is a identical copy of the data-disk, making it very easy to switch in case of a disaster. The disadvantage is that you have to have local access to the server (Pi) for attaching the backup-disk.

This backup will be done to a dedicated backup-disk, connected to the Pi it self, thus a server-based backup.

#### Steps to create a server-based backup
* format a disk dedicated for RPMS-backups (you only have to do this once):
  * connect your (empty) backup-disk to your PC
  * `wget https://github.com/markbaaijens/rpmusicserver/raw/master/scripts/format-usbdisk.sh -O /tmp/format-usbdisk.sh && chmod +x /tmp/format-usbdisk.sh && sudo /tmp/format-usbdisk.sh`
    * enter your (personal) password of the client-machine
  * follow the instructions to format as a BACKUP-disk
* engage the backup:
  * connect your backup-disk to the Pi
  * in the web-interface, under Backup, click Backup
  * disconnect backup-disk

#### Viewing backup-data on the usbbackup-disk
In case of a server-based backup, your backup will be made to a separate backup-disk. You can view the data on this disk, either online or offline:

* for viewing _online_, the backup-disk has to be attached to the Pi. Simply point your file esplorer to `smb://rpms/Backup` and than you can view all the files on that disk.
* for viewing _offline_, the backup-disk has to be attached to your own PC or laptop. The backup-disk is formatted as ext4 so this format is natively supported on Linux, thus being plug-and-play. Windows however requires additional drivers for viewing ext-drives. And worse, MacOS does NOT support ext4 at all! (despite extX being open-source/open-standard).

### Remote backup
The advantage of the remote backup is that you can use a protocol at wish, be it ssh/rsync or syncthing (which is built-in in RPMS) or SMB. The disadvantage of a remote backup is that in case of a disaster, it is a lot more work to get up-and-running again.

Note that system-data is also present on the data-part ('Public') in the form of a file rpms-system.zip. Thus, as you backup the user-data, you also backup the system-files resulting in a full backup. 

For a backup using rsync over SSH, here is a example-script:<br>
`#!/bin/bash`<br/> 
`rsync --progress --delete -rtv --max-size=4GB --modify-window=2 --exclude Downloads \`<br/> 
`	pi@rpms:/media/usbdata/user/* \`<br/> 
`	/media/$USER/<disklabel of backup-disk>/backup/user`<br/> 
`sync`<br/> 

## Disaster Recovery
Disaster can come from anywhere: a broken Pi (very unlikely), a corrupt SD-card or a data-disk which get broken. In each case, the solution within RPMS is very simple

### Broken Pi (very unlikely)
Steps to get back on track:
* obtain a new Pi which meets the system requirements (see above)
* swap the SD-card from the defect Pi
* connect your data-disk
* boot up the new Pi and you are ready to go

You may possibly need to [reconnect player(s)](https://github.com/markbaaijens/rpmusicserver#reconnect-players-after-lms-migration)

### Corrupt SD-card
Steps to get back on track:
* if the hardware is damaged, obtain a new card, otherwise, use the same card
* burn and install RPMS onto the card (see above for instructions)

* now you are ready to go

You may possibly need to [reconnect player(s)](https://github.com/markbaaijens/rpmusicserver#reconnect-players-after-lms-migration)

### Data-disk crash
_In case of a server-based backup_, you are 'lucky': b/c the backup-disk is an exact copy aka mirror of the data-disk and even of the same disk-type (ext4), you can simply swap them once the data-disk has been crashed. 

Steps to get back on track:
* rename the label of the backup-disk from `usbbackup` to `usbdata` 
  * use your favourite disk-tool (Disks, gparted, etc.)
* connect the disk to the Pi and boot up

By now, the backup-disk has been automagically changed into a data-disk by now and you can go on from the last backup that you made.

_In case of a remote backup_, you have more work to do: 
* reformat a (new) disk for usbdata-usage (see instructions above)
* copy all data from the remote backup location to the data-disk under '/user'
* unzip rpms-system.zip (this file is present in the root of the data-backup)
* copy the contents of rpms-system.zip to /rpms
* attach the newly formatted and populated data-disk to the Pi
* reboot and you are back in business

Remember to make a backup to a new backup-disk immediately!

## Development

### Update from another git branch
By default, the update-mechanism looks at the `master` branch on github. However, it is possible to override the `master` branch version, by setting the desired branch version to a different value. 

In most cases this is the `develop` branch. Once set, you can update to the latest developer-features. But b/c this is considered as experimental (non-stable), use this option with precaution!

To switch version from `master` branch to e.g. `develop` branch:
* `ssh pi@rpms "sudo bash -c 'echo \"develop\" > /media/usbdata/rpms/config/update-branch.txt'"`

Once the file `update-branch.txt` has been set, the update-button in the web-interface becomes active. Click on it and it will update rpms to the latest version on `develop`. 

You can also opt to update through ssh on rpms: 
* `ssh pi@rpms`
* `sudo update-rpms`

For returning to the `master` branch version simply delete the `update-branch.txt` file:
* `ssh pi@rpms "sudo bash -c 'rm /media/usbdata/rpms/config/update-branch.txt'"`

Note. Once an override is active, the current and available version do not play a role anymore.

Note. If local DNS does not work, the hostname`rpms` has to be replaced by the ip-address of that machine. See [Check your network if local DNS works](https://github.com/markbaaijens/rpmusicserver#check-your-network-if-local-dns-works) for details.

### Build development version with separate hostname
A regular install of rpms results in a Pi with hostname `rpms`, which is fine. As a developer, you want to test your code on a different machine than the one in production, on a second Pi; but having two machines within the network with the same hostname, results in errors. 

You can opt for using `rpmsdev` as the hostname for that second Pi. This is done while burning the SD-card, as the first step in the installation process [Installation of RPMS on a Pi](https://github.com/markbaaijens/rpmusicserver#installation-of-rpms-on-a-pi)<br/> 

* While burning the SD-card:
  * Select a type: choose D for Development

The other steps in the installation process stay the same. In the end, this result in a Pi with a hostname `rpmsdev`, so you can easily distinquish and address the two, development (`rpmsdev`) and production (`rpms`). From now on, you can reach the development-server on `rpmsdev`.

Note. It must be clear that if you do not have a production/live machine for rpms in your network and you are using the installed Pi solely for testing purposes, there is no need to have a different hostname, the standard `rpms` will do just fine.

Tip. In case hostnames `rpms` and `rpmsdev` get mixed up, try to flush DNS:
  * `sudo systemd-resolve --flush-caches`

### Update and install from local files  
As a developer, you want to test your changes on a physical machine (Pi). As the changes in the code are usually done on a different machine than the one on which the test takes places, you have to have a way to transfer your code to the (test) Pi and install them to see the result.

#### To have the code locally on your development-machine
* clone/download the git-repo from [github](https://github.com/markbaaijens/rpmusicserver) (instructions can be found there)
* place the code in a folder, something like `~/source/rpmusicserver`
* switch to branch `develop`

#### Copy local code to a Pi and install the (changed) code
* `cd <source-folder of rpmusicserver>`
* `rsync -r ./* pi@rpmsdev:/tmp/rpmusicserver`
  * password: `rpms`
* `ssh pi@rpmsdev "sudo chmod +x /tmp/rpmusicserver/scripts/* && sudo /tmp/rpmusicserver/scripts/install-rp.sh"`  
  * password: `rpms`

Note. The transferred code is dependent on the chosen git-branch. By changing the branch, you can transfer and test any code in any branch. 

Note. You can also do this 'trick' in a live, production-environment, but than you must know what you are doing, so don't try this at home! Usually, a production-machine is updated through the regular update-mechanism, in which code is retreived from the git-repo on github (be it the master-branch or, if overridden, by another branch, usually develop). 

Note. If local DNS does not work, the hostname`rpmsdev` must be replaced by the ip-address of that machine. See [Check your network if local DNS works](https://github.com/markbaaijens/rpmusicserver#check-your-network-if-local-dns-works) for details.    

### Local test-environment on your development-machine
Testing on a (second) machine/Pi is the ultimate test, but to quickly see your changes in the web-interface (api or web) on your development-machine, we can setup an environment for exactly that. 

In short, you have to open two terminals, each running a web-service, one running the api, the second running the web-UI:
* open a terminal
  * `cd <source-folder of rpmusicserver>/web-interface/api`
  * `python3 controller.py`
* open a second terminal
  * `cd <source-folder of rpmusicserver>/web-interface/web`
  * `python3 controller.py`
* for the web-UI, point your browser to `http://localhost:1080` 
* you can access the api:
  * point your browser to `http://localhost:5000`
  * cli: `curl http://localhost:5000`

Note. This environment is very limited b/c not all components which the code interacts with, such as disks or docker-containers or the Pi itself, are not available (however, you can spoof some of those components). But for seeing changes in the UI, this works just fine.

### Local LMS-player
As a developer, it is usefull to have at least one player which can connect to the LMS-server. We can easily transform a regular laptop or PC to a local player, just for testing purposes.

Steps for installing a local player:
- install squeezelite
  - `sudo apt install squeezelite`
- start player
  - `squeezelite -o default -z -n "Local"`
- stop player
  - `sudo kill $(ps -ef | grep squeeze | grep -v grep | awk '{print $2}')`

### List of API requests 
  * `curl rpms:5000/api/GetApiList`
  * http://rpms:5000/api/GetApiList

## Migrating to 1.0
Coming from any version below 1.0, you cannot migrate through the usual upgrade-command b/c the upgrade will introduce breaking changes which turn your system into a broken one. Further more, b/c we moved the OS from 32-bit to 64-bit, a new image-burn is needed.

### Steps to migrate to 1.0

(1) Burn a SD-card
- burn a SD-card on a new card on your local computer as if it is a fresh install
  - see [Steps to install RPMS on your Pi](https://github.com/markbaaijens/rpmusicserver#steps-to-install-rpms-on-your-pi) under 'Burn SD-card' for instructions
- card considerations
  - by taking a new card, you have a fall-back if things go wrong
  - you might use a bigger card b/c the [System requirements](https://github.com/markbaaijens/rpmusicserver#system-requirements) concerning the size of the card have been changed

(2) Convert your system
- backup your system
  - create a server-backup
  - optional: create remote backup
- delete entries in SyncThing
  - copy syncthing-config for later reference
    - `ssh pi@rpms "cat /media/usbdata/rpms/config/docker/syncthing/config.xml" > ~/synthing-config.txt`
  - locations will be changed:
    - /data/Muziek => /data/music
    - /data => /data/public     
  - record the folder-config functionally
    - sync-method (S Send, R Receive, S/R Send and receive)
    - current base folder (say /data/Muziek/xxx)
    - new base folder (say /data/music/xxx)
    - current subscribers
  - delete all folders in SyncThing
    - choose Discard when deleting folder (so that it can be added automatically later)
- ssh to rpms 
  - `ssh pi@rpms`
- kill all containers
  - `sudo kill-docker`
- rename folders
  - `sudo mv /media/usbdata/user/Publiek /media/usbdata/user/public`
  - `sudo mkdir /media/usbdata/user/music -p`
  - `sudo mv /media/usbdata/user/public/Muziek/* /media/usbdata/user/music`
  - `sudo rmdir /media/usbdata/user/public/Muziek`
  - `tree -d -L 2 /media/usbdata/user  # To check`
- convert transcoder-settings
  - `sudo sed -i -e 's/Publiek/public/g' /media/usbdata/rpms/config/transcoder-settings.json`
  - `sudo sed -i -e 's/public\/Muziek/music/g' /media/usbdata/rpms/config/transcoder-settings.json`
  - `cat /media/usbdata/rpms/config/transcoder-settings.json  # To check`
- stop the server
  - `sudo halt-server`  

(3) Install the new SD-card, boot the Pi and finish the installation
- put the new SD-card into the Pi and boot-up
- do an install, just like doing a new install of RPMS
  - see [Steps to install RPMS on your Pi](https://github.com/markbaaijens/rpmusicserver#steps-to-install-rpms-on-your-pi) under 'Installation' for instructions
- re-create folders in SyncThing if needed, with these new locations:
  - /data/Muziek => /data/music
  - /data => /data/public 

(4) Check system if all is working well: 
- Samba-shares
- LMS
- Transmission
- all pages and actions in the web-interface

**Optional**

- to speedup server-backup
  - `ssh pi@rpms`
  - `sudo mv /media/usbbackup/user/Publiek /media/usbbackup/user/public`
  - `sudo mkdir /media/usbbackup/user/music -p`
  - `sudo mv /media/usbbackup/user/public/Muziek/* /media/usbbackup/user/music`
  - `sudo rmdir /media/usbbackup/user/public/Muziek`
  - `tree -d -L 2 /media/usbbackup/user  # To check`
- local computer
  - manually modify local script for external backup if needed
  - modify bookmarks to shares


