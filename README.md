# sensoball

## Install

Make sure you have `python3.5` and `pip-3.5` installed,

```
$ sudo apt-get install python3
$ curl 'https://bootstrap.pypa.io/get-pip.py' | sudo python3 -
```

Next, install the dependencies,

```
$ sudo pip install -r requirements.txt
```

Finally, if you want to update the sensoball's init.lua with new AP information, run

```
$ python3 write_init.py /dev/ttyUSB0 init.lua <ssid> <wpa_password>
```

## Running

Simply type,

```
$ python3 web.py --hostname=<hostname_ip>
```

where `<hostname_ip>` is the IP address you'd like the sensoball to connect to.
You can go to [localhost:8081/static/d3.html](localhost:8081/static/d3.html) to
see a rendered visualization of sensoball data.


If you'd like to see all boards connected to your network, 

```
$ python3 multicast_listen.py
```
