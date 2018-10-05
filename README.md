# socksproxy :+1:


A flexible asynchronous socks4 / socks5 proxy written in pure python

This proxy module can be used as a full blown proxy or the classes can be used to provide a interface to socks4 or/and socks5

### usage:


**default settings**
```python
import socksproxy

socks5proxy = socksproxy.Socks5()
socks5proxy.start()
```


**set specific listen host, port, and not block while serving**
```python
import socksproxy
from asyncio import get_event_loop, sleep
socks4proxy = socksproxy.Socks4(listen_host='0.0.0.0', listen_port=1080)
socks4proxy.start(keep_serving=False)

# run other functions, emulated by sleep
get_event_loop().run_until_complete(sleep(20))
```
