import argparse
from asyncio import (all_tasks, get_event_loop, start_server)

from . import __description__
from ._socks4 import Socks4
from ._socks5 import Socks5


def check_interrupt(loop):
    loop.call_later(.1, check_interrupt, loop)


async def proxy_dispatcher(reader, writer):
    version = (await reader.read(1))[0]
    if 4 < version <= 5:
        print('request assigned to socks5 proxy')
        await Socks5.handle_client(reader, writer, 5)
    elif 5 > version >= 4:
        print('request assigned to socks4 proxy')
        await Socks4.handle_client(reader, writer, 4)


def get_args():
    args = argparse.ArgumentParser(
        prog='socksproxy',
        add_help=True,
        epilog=__description__
        #  epilog='asynchroneous socks proxy server that turns running machines into fast socks4(a) or socks5(h) proxies.'
    )
    args.add_argument('-l', '--listen-host',
                      dest='listen_host',
                      type=str,
                      default='0.0.0.0',
                      help='ip/host to listen on')
    args.add_argument('-p', '--listen-port',
                      dest='listen_port',
                      type=int,
                      default=1080,
                      help='port to listen on')
    return args.parse_args()


def run_proxy():
    args = get_args()
    loop = get_event_loop()
    loop.call_soon(check_interrupt, loop)
    try:
        server = get_event_loop().run_until_complete(start_server(proxy_dispatcher, args.listen_host, args.listen_port))
        for s in server.sockets:
            print('* socks server listening on {}:{}'.format(*s.getsockname()))
        loop.run_forever()
    except KeyboardInterrupt:
        print('received exit signal (ctrl+c)')
    except:
        pass
    finally:
        print('cancelling tasks')
        [t.cancel() for t in all_tasks(loop)]
        loop.run_until_complete(
            loop.shutdown_asyncgens()
        )
        print('bye')
