# raspi

## enable ssh
```
touch ssh
```

## enable usb access
append to `/config.txt`
```
# usb access
dtoverlay=dwc2
```
add to `/cmdline.txt` after `rootwait`
```
modules-load=dwc2,g_ether
```

## ssh key access
```
cd ~
mkdir .ssh && chmod 700 .ssh
touch .ssh/authorized_keys && chmod 600 .ssh/authorized_keys
# append public key to authorized_keys
```
```
sudo vim /etc/ssh/sshd_config
```
```
ChallengeResponseAuthentication no
PasswordAuthentication no
UsePAM no
```
```
sudo /etc/init.d/ssh restart # or sudo reboot
```

## setting wifi up via the command line
https://www.raspberrypi.org/documentation/configuration/wireless/wireless-cli.md

## camera
```
raspi-config
```

## nodejs
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

## docker
```
# TBD
```

## 5 inch hdmi display

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
