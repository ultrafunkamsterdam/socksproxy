import socket
from asyncio import (gather, get_event_loop, open_connection, start_server)
from ipaddress import ip_address
from struct import calcsize, pack, unpack



class Socks4:
    """
    Socks4 proxy class
    """


    def __init__(self, listen_host="127.0.0.1", listen_port=1080):
        """
        Socks4 constructor
        :param str listen_host: host to listen on (default: 127.0.0.1)
        :param int listen_port: port to listen on (default: 1080)
        """
        self.listen_host = listen_host
        self.listen_port = listen_port
        self.id = id(self)
        self.server = None


    @classmethod
    async def handle_client(cls, reader, writer, version=None):
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


        def write_reply(code_int, reply_version=0, dst_port=0, dst_host_ip="0.0.0.0"):
            """
            Writes a socks4 reply
            :param int code_int: return code.
            :param int reply_version: reply-version, not socks version. (default: 0)
            :param int dst_port: port number of requested host
            :param str dst_host_ip: ip of requested host
            """
            byte_string = pack(">BBH", reply_version, code_int, dst_port)
            byte_string += ip_address(dst_host_ip).packed
            writer.write(byte_string)


        async def read(fmt):
            """
            Read from the byte stream
            :param str fmt: struct format specifier
            :return tuple:
            """
            data = await reader.read(calcsize(fmt))
            return unpack(fmt, data)

        if version:
            cmd, port = await read(">BH")
        else:
            version, cmd, port = await read(">BBH")
        host = await reader.read(4)
        host = socket.inet_ntoa(host)
        null = await reader.readuntil(b"\x00")

        if host.startswith("0.0.0"):
            hostname = (await reader.readuntil(b"\x00"))[:-1].decode()
            if hostname.endswith(".onion"):
                print("this is a tor address : ", hostname)
                writer.write_eof()
                return
            host = socket.gethostbyname(hostname)

        remote_reader, remote_writer = await open_connection(host=host, port=port)
        write_reply(90, dst_port=port, dst_host_ip=host)
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
            print('socks4 server listening on {}:{}'.format(*s.getsockname()))
        if keep_serving:
            get_event_loop().run_forever()
