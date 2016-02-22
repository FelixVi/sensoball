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

Finally, if you want to update the sensoball's init.lua with new AP information
or a new board name, run

```
$ python3 write_init.py /dev/ttyUSB0 init.lua <ssid> <wpa_password> <board_name>
```

## Running

Just run,

```
$ python3 web.py --port=8080
```

You can go to [localhost:8080/static/d3.html](localhost:8080/static/d3.html) to
see a rendered visualization of sensoball data.  The API will connect to the
first board it finds (or you can provide the optional flag `--board-name` to
web.py to specify a board)


If you'd like to see all boards connected to your network, 

```
$ python3 multicast_listen.py
```
