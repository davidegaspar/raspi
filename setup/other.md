# other stuff (review)

#### docker-compose (didn't work last time)

```
sudo apt update
sudo apt install -y python python-pip libffi-dev python-backports.ssl-match-hostname
sudo pip install docker-compose
```

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
