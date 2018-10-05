import socket
from asyncio import (gather, get_event_loop, open_connection, start_server)
from ipaddress import ip_address
from struct import calcsize, pack, unpack

# __all__ = ['Socks5']
#

class Socks5:
    """
    Socks5 proxy class
    """

    NO_ADDR = '0.0.0.0'
    ATYP_IPv4 = 0x01
    ATYP_DNS = 0x03
    ATYP_IPv6 = 0x04


    def __init__(self, listen_host="127.0.0.1", listen_port=1080):
        """
        Socks5 constructor
        :param str listen_host: host to listen on (default: 127.0.0.1)
        :param int listen_port: port to listen on (default: 1080)
        """
        self.listen_host = listen_host
        self.listen_port = listen_port
        self.id = id(self)
        self.server = None


    @classmethod
    async def handle_client(cls, reader, writer, passed=False):
        """
        Handles a client connection
        :param StreamReader reader: streamreader instance passed by the server
        :param StreamWriter writer: streamwriter instance passed by the server
        """


        async def pipe(r, w, bufsize=2048, name=None):
            """
            Pipe 2 streams to each other
            :param StreamReader r: StreamReader instance
            :param StreamWriter w: StreamWriter instance
            :param int bufsize: Buffer size in bytes
            :param name: name of the piped connection. examples : "incoming", "outgoing"
            """
            try:
                data = await r.read(bufsize)
                while data:
                    w.write(data)
                    print("pipe {} = ".format("" if not name else " to " + name), data)
                    data = await r.read(bufsize)
            except Exception as e:
                pass


        def write_reply(code_int, reply_version=5, atyp=cls.ATYP_IPv4, host_ip=cls.NO_ADDR, port=0):
            """
            Writes a Socks5 reply
            :param int code_int: return code.
            :param int reply_version: reply-version (default: 5)
            :param int atyp: address type of requested host (ip4, dns or ip6)
            :param bytes host_ip: ip address of requested host
            :param int port: port number of requested host
            """
            byte_string = pack(">BBBB", reply_version, code_int, 0, atyp)
            byte_string += ip_address(host_ip).packed
            byte_string += pack("!H", port)
            writer.write(byte_string)


        async def read(fmt):
            """
            Read from the byte stream
            :param str fmt: struct format specifier
            :return tuple:
            """
            data = await reader.read(calcsize(fmt))
            return unpack(fmt, data)


        version = 5
        num_methods = (await read(">B"))[0]
        methods = await read("!" + "B" * num_methods)

        # reply the server selected method "no auth required"
        writer.write(pack("!BB", version, 0))

        version, cmd, resv, atyp = await read(">BBBB")
        if atyp == cls.ATYP_IPv4:
            ip_packed = await reader.read(4)
            port = (await read("!H"))[0]
            ip_addr = socket.inet_ntop(socket.AF_INET, ip_packed)
            hostname = None
        elif atyp == cls.ATYP_IPv6:
            ip_packed = await reader.read(16)
            port = (await read("!H"))[0]
            ip_addr = socket.inet_ntop(socket.AF_INET6, ip_packed)
            hostname = None
        elif atyp == cls.ATYP_DNS:
            hostname_len = (await read("!B"))[0]
            hostname = (await read("!{}s".format(hostname_len)))[0]
            port = (await read("!H"))[0]
            ip_addr = None
        else:
            write_reply(0x08)
            print(
                "Address type could not be determined from stream. "
                "It should be either IPV4, IPV6 or DNS name. "
                "Request discarded"
            )
            return

        if hostname:
            if hostname.endswith(b".onion"):
                print("this is a tor address : ", hostname)
                writer.write_eof()
                return
            if not ip_addr:
                ip_addr = socket.gethostbyname(hostname)
        else:
            hostname = socket.gethostbyaddr(ip_addr)

        remote_reader, remote_writer = await open_connection(host=ip_addr, port=port)
        write_reply(0x00, port=port, host_ip=ip_addr, atyp=cls.ATYP_IPv4)

        tasks = [
            pipe(reader, remote_writer, name="outgoing"),
            pipe(remote_reader, writer, name="incoming"),
        ]
        await gather(*tasks)
        writer.write_eof()


    def start(self, keep_serving=True):
        """
        Start serving
        """
        self.server = get_event_loop().run_until_complete(
            start_server(self.handle_client, self.listen_host, self.listen_port)
        )
        for s in self.server.sockets:
            print('Socks5 server listening on {}:{}'.format(*s.getsockname()))
        if keep_serving:
            get_event_loop().run_forever()
