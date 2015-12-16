# camera

## setup
https://www.raspberrypi.org/documentation/usage/camera/README.md

## cli
https://www.raspberrypi.org/documentation/usage/camera/raspicam/README.md

## motion
#### install
```
$ sudo apt-get install motion
$ sudo apt-get install libjpeg62 libjpeg62-dev libavformat-dev libavcodec-dev libavutil-dev libc6-dev zlib1g-dev libmysqlclient-dev libpq-dev
$ mkdir mmal
$ cd mmal
$ wget https://www.dropbox.com/s/jw5r1wss32tdibb/motion-mmal-opt.tar.gz
$ tar -zxvf motion-mmal-opt.tar.gz
$ cd motion-mmal
$ sudo nano motion-mmalcam.conf
```
#### config `<-- stopped here`
```
width 640
height 480
framerate 6
target_dir /home/pi/cam
output_pictures off
text_left Pi-cam %t
logfile  /home/pi/mmal/motion.log
ffmpeg_output_movies on
```
#### run
```
$ ./motion-mmal -n -c motion-mmalcam.conf
```
#### run new
```
sudo scp davidegaspar@192.168.1.90:/Users/davidegaspar/motionx.conf montionx3.conf
sudo ./motionx -n -c motionx.conf
```

#### startup
```
sudo cp /home/cookie/sd/camx/mx.conf /etc/motion.conf
sudo cp /home/cookie/sd/camx/motionx /usr/bin/motion
sudo nano /etc/default/motion
sudo touch /tmp/motion.log
sudo chmod 775 /tmp/motion.log
```
> logfile /tmp/motion.log

#### fix permissions so the group user can access the cam folder and the log
```
sudo scp davidegaspar@192.168.1.90:/Users/davidegaspar/motionx.conf /etc/motion.conf
sudo usermod -a -G motion cookie
sudo chmod 664 /tmp/motion.log
sudo chgrp motion /home/cookie/sd/cam
sudo chmod 775 sd/cam
```

#### clean log
```
sudo cat /dev/null > /tmp/motion.log
```

#### start stop daemon
```
sudo /etc/init.d/motion start
sudo /etc/init.d/motion stop
```

## cron
```
$ crontab -e
```
```
30 8 * * 1,2,3,4,5 sudo /etc/init.d/motion start
30 20 * * 1,2,3,4,5 sudo /etc/init.d/motion stop
```
> mon-fri 8300 2000

**other**
```
*/5 * * * * /etc/init.d/motion restart &>> /home/cookie/sd/cam/cam.log
```

#### docs
http://www.lavrsen.dk/foswiki/bin/view/Motion/ConfigFileOptions


## stream
http://www.raspberry-projects.com/pi/pi-hardware/raspberry-pi-camera/streaming-video-using-vlc-player
```
sudo apt-get install vlc
raspivid -o - -t 0 -n | cvlc -vvv stream:///dev/stdin --sout '#rtp{sdp=rtsp://:8554/}' :demux=h264
raspivid -o - -t 0 -n -w 600 -h 400 -fps 12 | cvlc -vvv stream:///dev/stdin --sout '#rtp{sdp=rtsp://:8554/}' :demux=h264
```
rtsp://192.168.1.56:8554/

**this works o/**
http://www.rs-online.com/designspark/electronics/knowledge-item/raspberry-pi-camera-setup
```
sudo nc -l 5001 | mplayer -fps 12 -cache 1024 -
sudo raspivid -vf -hf -w 600 -h 400 -fps 12 -t 999999 -o - | nc 192.168.1.90 5001
```

## other tutorials
http://www.instructables.com/id/Raspberry-Pi-as-low-cost-HD-surveillance-camera/?ALLSTEPS
https://rbnrpi.wordpress.com/project-list/setting-up-wireless-motion-detect-cam/
