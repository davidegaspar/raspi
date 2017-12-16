# network

## setting wifi up via the command line
https://www.raspberrypi.org/documentation/configuration/wireless/wireless-cli.md

## static ip `<-- needs review`
```
$ sudo ifconfig
$ netstat -nr
$ sudo nano /etc/network/interfaces
```
```
iface eth0 inet static
address 192.168.1.56
netmask 255.255.255.0
network 192.168.1.0
broadcast 192.168.1.255
gateway 192.168.1.1
```
```
$ sudo reboot
```
