# usb
## create
#### find sda or sda1
```
$ sudo blkid
```
or
```
$ dmesg | tail -n 17
```

#### unmout to make sure
```
$ sudo umount /dev/sda1
```

#### format ext4 name=‘Sync’
```
$ sudo mkfs.ext4 /dev/sda1 -L Sync
```

#### mount
```
sudo mkdir /home/pi/sandisk
sudo mount -t ext4 /dev/sda1 /home/pi/sandisk
```

#### backup fstab
```
$ sudo cp /etc/fstab /etc/fstab.backup
```

#### add to fstab
```
$ sudo nano /etc/fstab
```
```
/dev/sda1 /home/pi/sandisk ext4 rw,defaults 0 0
```

## clone usb2usb partition
```
$ sudo dd if=/dev/sda1 of=/dev/sdb1
```

## clone usb2usb drive
```
$ sudo dd if=/dev/sda of=/dev/sdb
```

## over a network
```
$ dd if=/dev/sda | ssh username@host "dd of=/dev/sda"
```

## from a network
```
$ ssh username@host "dd if=/dev/sda" | dd of=/dev/sda
```

## help
http://elinux.org/RPi_Adding_USB_Drives

#### more complete
https://wiki.archlinux.org/index.php/disk_cloning
```
$ sudo dd if=/dev/sda of=/dev/sdb bs=512 conv=noerror,sync
```

## show progress
open new terminal
```
$ sudo kill -USR1 `pgrep ^dd`
```
or periodic (10min)
```
$ watch -n600 'sudo kill -USR1 `pgrep ^dd`'
```

## list disks and partitions
```
$ sudo fdisk -l
$ lsblk
```
