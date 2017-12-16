# pie spy

## install
http://picamera.readthedocs.io/en/release-1.12/recipes1.html
```
sudo apt-get install python-picamera
sudo pip install picamera # or
python main.py
```

## stream
raspi
```
python stream.py
```
osx
```
/Applications/VLC.app/Contents/MacOS/VLC tcp/h264://192.168.2.19:8000
```

## docker
```
docker build -t piespy:1 .
```
