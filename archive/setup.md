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

```
echo "
# usb access
dtoverlay=dwc2
" >> config.txt
```

```
sed -i '' 's/rootwait/rootwait modules-load=dwc2,g_ether/g' cmdline.txt
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
nano .ssh/authorized_keys
```

- **mac**

```
pbcopy < ~/.ssh/id_rsa.pub
```

- **pi**

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

#### 4. setup wifi

https://www.raspberrypi.org/documentation/configuration/wireless/wireless-cli.md

```
sudo raspi-config
```

#### 5. install docker

```
curl -sSL https://get.docker.com | sh
```

#### 6. install git

```
apt install -y git tree
```

#### 6. install tree

```
apt install tree
```
