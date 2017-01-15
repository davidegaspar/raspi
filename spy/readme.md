# s.py

## dependencies
```bash
sudo apt-get update
# python3 + pip3
curl -sS https://get.pimoroni.com/blinkt | bash
sudo apt-get install python-gpiozero python3-gpiozero
sudo apt-get install python-picamera python3-picamera
```

## service
```
cp spy /etc/init.d/spy
sudo chmod +x /etc/init.d/spy
sudo /etc/init.d/spy start
sudo /etc/init.d/spy stop
sudo update-rc.d spy defaults
```
