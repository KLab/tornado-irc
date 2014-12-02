import socket
from collections import namedtuple

import tornado.iostream
import tornado.ioloop
import tornado.gen


_DEBUG = False

Event = namedtuple("Event", "raw line source nick user host code args")


class IRCClient:
    def __init__(self, address, nick, user, *, io_loop=None, sock_family=socket.AF_INET):
        self.io_loop = io_loop or tornado.ioloop.IOLoop.current()
        self.address = address
        self.nick = nick
        self.user = user
        self.sock_family = sock_family
        #: :type: tornado.iostream.IOStream
        self.stream = None

    @tornado.gen.coroutine
    def connect(self):
        if self.stream is not None:
            self.stream.close()
        s = socket.socket(family=self.sock_family)
        self.stream = tornado.iostream.IOStream(s, io_loop=self.io_loop)
        yield self.stream.connect(self.address)
        self.send_message("NICK " + self.nick)
        self.send_message("USER %s 0 * :%s" % (self.user, self.user))

    @tornado.gen.coroutine
    def _read_message(self):
        #: :type: bytes
        raw = yield self.stream.read_until(b'\n')
        raw = raw.rstrip(b'\r\n')
        if _DEBUG:
            print("Received: ", raw)
        #: :type: str
        line = raw.decode('utf-8')

        source = nick = user = host = None
        msg = line

        if line[0] == ':':
            pos = line.index(' ')
            source = line[1:pos]
            msg = line[pos+1:]
            i = source.find('!')
            j = source.find('@')
            if i>0 and j>0:
                nick = source[:i]
                user = source[i+1:j]
                host = source[j+1:]

        sp = msg.split(' :', 1)
        code, *args = sp[0].split(' ')
        if len(sp) == 2:
            args.append(sp[1])

        event = Event(raw, line, source, nick, user, host, code, args)
        if _DEBUG:
            print("Event: ", event)
        return event

    @tornado.gen.coroutine
    def read_message(self):
        while True:
            event = yield self._read_message()
            if event.code == "PING":
                self.send_message("PONG %s" % (event.args[0],))
            else:
                return event

    def send_message(self, line: str):
        if isinstance(line, str):
            line = line.encode('utf-8')
        if _DEBUG:
            print("Sending:", line)
        self.stream.write(line + b'\r\n')

    def close(self):
        self.stream.close()


@tornado.gen.coroutine
def connect(address, nick, user, *, io_loop=None, sock_family=socket.AF_INET):
    client = IRCClient(address, nick, user, io_loop=io_loop, sock_family=sock_family)
    yield client.connect()
    return client


if __name__ == '__main__':
    _DEBUG = True
    import sys

    @tornado.gen.coroutine
    def main():
        host, nick, user, channel = sys.argv[1:]
        port = 6667
        if ':' in host:
            host, port = host.split(':')
            port = int(port)

        conn = yield connect((host, port), nick, user)
        conn.send_message("JOIN #%s" % (channel,))
        while True:
            yield conn.read_message()

    tornado.ioloop.IOLoop.current().run_sync(main)
