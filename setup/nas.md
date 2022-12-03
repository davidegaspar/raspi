# NAS

## 1. Install

```sh
sudo apt-get update
sudo apt install samba samba-common-bin
```

## 2. Config

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

## 3. Verify

```sh
# macOS (Finder > cmd+K)
smb://$RPI_HOSTNAME.local/chocobo
```
