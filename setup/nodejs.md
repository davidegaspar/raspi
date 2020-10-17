# nodejs

## install (new)
```
curl -sL https://deb.nodesource.com/setup_12.x | sudo -E bash -
sudo apt-get install -y nodejs
node -v
```

## install (old)
```
curl -O https://nodejs.org/dist/v12.13.1/node-v12.13.1-linux-armv7l.tar.xz
mkdir -p /usr/local/lib/nodejs
tar -xJvf node-v12.13.1-linux-armv7l.tar.xz -C /usr/local/lib/nodejs
ln -s /usr/local/lib/nodejs/node-v12.13.1-linux-armv7l/bin/node /usr/bin/node
ln -s /usr/local/lib/nodejs/node-v12.13.1-linux-armv7l/bin/npm /usr/bin/npm
rm node-v12.13.1-linux-armv7l.tar.xz
```
