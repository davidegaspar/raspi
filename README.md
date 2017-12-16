# raspi

## enable ssh
```
touch ssh
```

## enable usb access
add these lines to the `/config.txt` file
```
# usb access
dtoverlay=dwc2
```
add this to lines to the `/cmdline.txt` file after `rootwait`
```
modules-load=dwc2,g_ether
```

## setting wifi up via the command line
https://www.raspberrypi.org/documentation/configuration/wireless/wireless-cli.md

## docker
TBD

## 5 inch hdmi display

add these lines to the `/config.txt` file

```
# 5 inch display
#config_hdmi_boost=4
hdmi_force_hotplug=1
hdmi_cvt=800 480 60 6 0 0 0
hdmi_group=2
hdmi_mode=87
hdmi_drive=2
max_usb_current=1
#overscan_left=10
#overscan_right=10
#overscan_top=10
#overscan_bottom=10
#test_mode=5
#display_rotate=1
```
