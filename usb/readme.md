# usb access

add these lines to the `/config.txt` file

```
# usb access
dtoverlay=dwc2
```

add this to lines to the `/cmdline.txt` file after `rootwait`

```
modules-load=dwc2,g_ether
```

! cant connect to macOS

# ic2 enable (maybe?)
```
dtparam=i2c1=on
dtparam=i2c_arm=on
```
for now just use `raspi-config`

# enable ssh
```
touch ssh
```
