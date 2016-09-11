# scrollphat

```
sudo raspi-config
```
> 9 Advanced Options - A6 I2C - Enable

```
cd ~
git clone https://github.com/pimoroni/scroll-phat.git
cd scroll-phat/docker
./build_docker.sh
docker run -ti --privileged scroll-phat
```

```
docker run -ti --privileged scroll-phat python examples/test-all.py
docker run -ti --privileged scroll-phat python examples/life.py
docker run -ti --privileged scroll-phat python examples/simple-text-scroll.py "hello world"
```
