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
vi /etc/openvpn/credentials
# download linux file from https://member.hide.me/en/server-status
sed -i 's/auth-user-pass/auth-user-pass \/etc\/openvpn\/credentials/g' /etc/openvpn/nl.hideservers.net.ovpn
nohup openvpn --config /etc/openvpn/nl.hideservers.net.ovpn &
```

## reboot

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