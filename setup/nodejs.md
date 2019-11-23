# nodejs

## install
```
curl -O https://nodejs.org/dist/v12.13.1/node-v12.13.1-linux-armv7l.tar.xz
mkdir -p /usr/local/lib/nodejs
tar -xJvf node-v12.13.1-linux-armv7l.tar.xz -C /usr/local/lib/nodejs
ln -s /usr/local/lib/nodejs/node-v12.13.1-linux-armv7l/bin/node /usr/bin/node
ln -s /usr/local/lib/nodejs/node-v12.13.1-linux-armv7l/bin/npm /usr/bin/npm
rm node-v12.13.1-linux-armv7l.tar.xz
```
