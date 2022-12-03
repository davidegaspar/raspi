# transmission

## reference

- https://pimylifeup.com/raspberry-pi-transmission/
- https://help.ubuntu.com/community/TransmissionHowTo

```sh
sudo apt-get install transmission-cli transmission-common transmission-daemon
```

## daemon

```
sudo apt install transmission-daemon
sudo nano /etc/transmission-daemon/settings.json
```

```json
"download-dir": "/home/pi/.../dwn",
"incomplete-dir": "/home/pi/.../inc",
"incomplete-dir-enabled": true,
"rpc-authentication-required": false,
"port-forwarding-enabled": true,
"rpc-whitelist": "127.0.0.1,192.168.*.*",
```

**NOTE: this can be done with a nodejs script, merge object with defaults**

### change to pi user

```sh
sudo nano /etc/init.d/transmission-daemon
```

```txt
USER=pi
```

```sh
sudo nano /etc/systemd/system/multi-user.target.wants/transmission-daemon.service
```

```txt
User=pi
```

```sh
sudo systemctl daemon-reload
sudo chown -R pi:pi /etc/transmission-daemon
```

```sh
sudo mkdir -p /home/pi/.config/transmission-daemon/
sudo ln -s /etc/transmission-daemon/settings.json /home/pi/.config/transmission-daemon/
sudo chown -R pi:pi /home/pi/.config/transmission-daemon/
```

### reload

```
sudo systemctl reload transmission-daemon
```

### dump settings

```
transmission-daemon -d
```

```
hostname -I
```

## remote

## install

```
sudo apt install transmission-remote
```

### web

```
open http://<ip>:9091/transmission/web/
```

### list

```
transmission-remote <ip>:9091 -l
```

### add

```
transmission-remote <ip>:9091 -a https://.../download/1289266.torrent
```

### stop

```
transmission-remote --exit
```
