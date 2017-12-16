# os

## install in sd card
#### find
```
$ diskutil list
```
#### unmount
```
$ diskutil unmountDisk /dev/disk3
```
#### write
```
$ sudo dd bs=1m if=2015-02-16-raspbian-wheezy.img of=/dev/rdisk3
```
or
```
bs=1M
```
#### eject
```
$ sudo diskutil eject /dev/rdisk3
```

#### fix permissions error
```
$ sudo diskutil partitionDisk /dev/disk3 1 MBR "Free Space" "%noformat%" 100%
```

#### check progress
Ctrl+T

## ssh remove warning
```
$ ssh-keygen -R 192.168.1.135
```

## update os
```
$ sudo apt-get update
$ sudo apt-get upgrade
$ sudo reboot
```

## disk space
```
$ ncdu -x <some folder>
$ du -s * | sort -nr | head
$ df -h
$ du -sch .[!.]* * |sort -h
```

## turn off
```
$ sudo shutdown -h now
$ sudo halt
```

## processes
```
$ ps aux | grep firef*
$ pgrep firefox
```
