# camera

## setup
https://www.raspberrypi.org/documentation/usage/camera/README.md

## cli
https://www.raspberrypi.org/documentation/usage/camera/raspicam/README.md

## motion

#### install

```
sudo apt-get install motion
sudo apt-get install libjpeg62
```

#### download, extract and move

```
wget https://www.dropbox.com/s/jw5r1wss32tdibb/motion-mmal-opt.tar.gz
tar zxvf motion-mmal-opt.tar.gz
sudo mv motion-mmal/motion /usr/bin/motion
sudo mv motion-mmal/motion-mmalcam.conf /etc/motion.conf
```

#### enable daemon

```
sudo nano /etc/default/motion
```

```
start_motion_daemon=yes
```

#### edit config

```
sudo nano /etc/motion.conf
```

```
daemon on
logfile /tmp/motion.log
width 640
height 480
framerate 5
pre_capture 5
post_capture 5
max_movie_time 600
output_pictures off
ffmpeg_output_movies on
text_left CAMERA %t
target_dir /home/pi/cam
```

#### permissions

```
-rw-r--r-- 1 pi pi 29904 Jan 31 18:17 /etc/motion.conf
-rwxr-xr-x 1 pi pi 320267 May 10  2014 /usr/bin/motion
-rw-r--r-- 1 motion motion 55770 Jan 31 18:48 /tmp/motion.log
drwxrwxr-x 2 pi motion   4096 Jan 31 18:48 /home/pi/cam
```

#### start/stop

```
sudo service motion start
tail -f /tmp/motion.log
sudo service motion start
```

#### live
go to http://pi.ip.address:8081 in the browser

#### clean log
```
sudo cat /dev/null > /tmp/motion.log
```

## disable led
```
sudo nano /boot/config.txt:
disable_camera_led=1
```

## cron (review)
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

## stream (review)
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

## references
http://www.instructables.com/id/Raspberry-Pi-as-low-cost-HD-surveillance-camera/?ALLSTEPS
https://rbnrpi.wordpress.com/project-list/setting-up-wireless-motion-detect-cam/
https://github.com/dozencrows/motion/tree/mmal-test
https://medium.com/@Cvrsor/how-to-make-a-diy-home-alarm-system-with-a-raspberry-pi-and-a-webcam-2d5a2d61da3d#.g9sflspsl
