# NAS

## install
```
sudo apt-get update
sudo apt install samba samba-common-bin
```

## config
```
mkdir -p /home/pi/chocobo
sudo nano /etc/samba/smb.conf
```
```
[chocobo]
path = /home/pi/chocobo
writeable=Yes
create mask=0777
directory mask=0777
public=no
```
```
sudo smbpasswd -a pi
sudo systemctl restart smbd
```

## connect
```
hostname -I
```
```
smb://0.0.0.0/chocobo
smb://raspberrypi.local/chocobo
```
