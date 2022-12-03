# Setup raspi (Dec 2022)

## 1. Install OS

Go to https://www.raspberrypi.com/software/ and download use Raspberry Pi Imager

Click `Advanced` (Gear) to setup the following:

- Set hostname - make sure it's a new one in your network
- Enable SSH - get public key `cat ~/.ssh/id_ed25519.pub | pbcopy`
- Configure wireless LAN

## 2. Remote access

```sh
arp -a # find device IP
export RPI_HOSTNAME="..."
ping $RPI_HOSTNAME.local
ssh pi@$RPI_HOSTNAME.local
```

## 3. Update/Upgrade

```sh
sudo apt update
sudo apt upgrade
```

## 4. Install packages

```sh
sudo apt-get install -y dnsutils git tree
```

## Reference

- [raspberrypi.com/documentation/computers/remote-access](https://www.raspberrypi.com/documentation/computers/remote-access.html#remote-access)

- [raspberrypi.com/documentation/computers/configuration.html#using-key-based-authentication](https://www.raspberrypi.com/documentation/computers/configuration.html#using-key-based-authentication)
