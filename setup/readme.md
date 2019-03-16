# Setup

#### 0. enable ssh

- download raspbian lite (no desktop or other crap) https://www.raspberrypi.org/downloads/raspbian/
- install etcher https://www.balena.io/etcher/
- flash image to sd card

#### 1. enable ssh
- **mac**
```
cd /Volumes/boot
touch ssh
```

#### 2. enable usb access
- **mac**
append to `config.txt`
```
# usb access
dtoverlay=dwc2
```
add to `cmdline.txt` after `rootwait`
```
modules-load=dwc2,g_ether
```

#### 3. connect to the pi

- pi Zero (usba port) <-> mac (micro usb data port)
- pi 2/3 (ethernet port) <-> mac (ethernet port)

- **mac**
```
ssh pi@raspberrypi.local
pi:raspberry
```

#### 3. add ssh key

- **pi**
```
cd ~
mkdir .ssh && chmod 700 .ssh
touch .ssh/authorized_keys && chmod 600 .ssh/authorized_keys
```

- **mac**
```
pbcopy < ~/.ssh/id_rsa.pub
```

- **pi**
```
nano .ssh/authorized_keys
```
```
sudo nano /etc/ssh/sshd_config
```
```
ChallengeResponseAuthentication no
PasswordAuthentication no
UsePAM no
```
```
sudo /etc/init.d/ssh restart # or sudo reboot
```

#### 4. wifi
https://www.raspberrypi.org/documentation/configuration/wireless/wireless-cli.md

## other stuff (review)

#### camera
```
raspi-config
```

#### nodejs
https://nodejs.org/en/download/
```
sudo su
cd /opt
uname -a
wget <url_for_armv6/7/8> -O nodejs.tar.xz
tar -xvf nodejs.tar.xz
ln -s /opt/nodejs/bin/node /usr/bin/node
ln -s /opt/nodejs/bin/npm /usr/bin/npm
node -v
npm -v
rm nodejs.tar.xz
```

#### aws
```
sudo apt-get install python-pip
sudo pip install awscli --upgrade --user
sudo ln -s ~/.local/bin/aws /usr/bin/aws
aws --version
```

#### docker
```
# TBD
```

#### 5 inch hdmi display

add these lines to the `/config.txt` file

```
# 5 inch display
#config_hdmi_boost=4
hdmi_force_hotplug=1
hdmi_cvt=800 480 60 6 0 0 0
hdmi_group=2
hdmi_mode=87
hdmi_drive=2
max_usb_current=1
#overscan_left=10
#overscan_right=10
#overscan_top=10
#overscan_bottom=10
#test_mode=5
#display_rotate=1
```
