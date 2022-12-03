# openvpn

## docs

- https://hide.me/en/vpnsetup/ubuntu/openvpn-command-line/

## setup

```sh
sudo -s
apt-get -y install openvpn
sudo reboot
```

```sh
touch /etc/openvpn/credentials
printf '%s\n' 'username' 'password' > /etc/openvpn/credentials
nano /etc/openvpn/credentials
# download linux file from https://member.hide.me/en/server-status
# needs login, manual download to macOS and drop into raspi via smb
cp <drop_dir>/nl.hideservers.net.ovpn /etc/openvpn/nl.hideservers.net.ovpn
sed -i 's/auth-user-pass/auth-user-pass \/etc\/openvpn\/credentials/g' /etc/openvpn/nl.hideservers.net.ovpn
```

## start

```sh
nohup openvpn --config /etc/openvpn/nl.hideservers.net.ovpn &
```

## Service (not working, does not start)

```sh
sudo vi /lib/systemd/system/HideMeOpenVPN.service
```

```sh
[Unit]
Description=Hide.me OpenVPN
After=multi-user.target

[Service]
Type=idle
ExecStart=/usr/sbin/openvpn --config /etc/openvpn/nl.hideservers.net.ovpn

[Install]
WantedBy=multi-user.target
```

```sh
sudo chmod 644 /lib/systemd/system/HideMeOpenVPN.service
sudo systemctl daemon-reload
sudo systemctl enable HideMeOpenVPN.service
```

```sh
sudo systemctl status HideMeOpenVPN.service
```

## verify

```sh
# txt browser
sudo apt-get install elinks
```

```sh
# whats my ip
sudo apt-get install dnsutils
dig +short myip.opendns.com @resolver1.opendns.com
# or
dig TXT +short o-o.myaddr.l.google.com @ns1.google.com
```

## Restart

```sh
sudo -s nohup openvpn --config /etc/openvpn/nl.hideservers.net.ovpn &
```
