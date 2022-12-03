# usb

## list

```
lsblk
```

## format

```
umount /dev/sda2
mkdir -p /media/usb/
mkfs.ext4 /dev/sda2 -L plex64
```

## mount

```
mount -t ext4 /dev/sda2 /media/plex
```

## mount on restart

```
cp /etc/fstab /etc/fstab.backup
nano /etc/fstab
# add this
/dev/sda2 /media/plex ext4 rw,defaults 0 0
```
