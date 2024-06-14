from classes.parallel import Parallel
from classes.log import Log as UnsafeLog
from multiprocessing import Manager, Value
import time
import socket
import json


# noinspection PyProtectedMember
class ConcurrentLog:
    __process = None

    def __init__(self):
        manager = Manager()
        ready = manager.Value('i', 0)
        self.__class__.__process = Parallel()
        self.__class__.__process.asynchronous_call(self.reader_proc, (ready,))
        while ready.value == 0:
            time.sleep(.1)
        self.__port = ready.value
        manager.shutdown()
        self.__started = True

    @staticmethod
    def reader_proc(ready: Value):
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serversocket.bind(('localhost', 0))
        serversocket.listen(1000)

        ready.value = serversocket.getsockname()[1]

        buf = b''
        while True:
            connection, address = serversocket.accept()
            temp_buf = connection.recv(256)
            if len(temp_buf) > 0:
                buf += temp_buf
                if buf[-1] == 10:
                    buf = buf[:-1].decode('UTF-8')
                    try:
                        msg = json.loads(buf)
                    except:
                        msg = ""
                    buf = b''

                    if len(msg) == 1 and msg[0] == "exit":
                        connection.close()
                        serversocket.close()
                        break
                    elif not isinstance(msg, list) or len(msg) < 2:
                        continue
                    else:
                        if msg[0] == "w":
                            UnsafeLog.warning(msg[1][0], *msg[1][1], **{'skip_formatting': True, **msg[1][2]})
                        elif msg[0] == "i":
                            UnsafeLog.info(msg[1][0], *msg[1][1], **{'skip_formatting': True, **msg[1][2]})
                        elif msg[0] == "e":
                            UnsafeLog.error(msg[1][0], *msg[1][1], **{'skip_formatting': True, **msg[1][2]})
                        elif msg[0] == "d":
                            UnsafeLog.debug(msg[1][0], *msg[1][1], **{'skip_formatting': True, **msg[1][2]})
                        elif msg[0] == "x":
                            UnsafeLog.exception(msg[1][0], *msg[1][1], **{'skip_formatting': True, **msg[1][2]})

    def warning(self, msg, *args, **kwargs) -> None:
        ret = UnsafeLog.warning(msg, *args, **{'return_only': True, 'frame_level': 3, **kwargs})
        self.__send(("w", (ret, args, kwargs)))

    def info(self, msg, *args, **kwargs) -> None:
        ret = UnsafeLog.info(msg, *args, **{'return_only': True, 'frame_level': 3, **kwargs})
        self.__send(("i", (ret, args, kwargs)))

    def error(self, msg, *args, **kwargs) -> None:
        ret = UnsafeLog.error(msg, *args, **{'return_only': True, 'frame_level': 3, **kwargs})
        self.__send(("e", (ret, args, kwargs)))

    def debug(self, msg, *args, **kwargs) -> None:
        ret = UnsafeLog.debug(msg, *args, **{'return_only': True, 'frame_level': 3, **kwargs})
        self.__send(("d", (ret, args, kwargs)))

    def exception(self, msg, *args, **kwargs) -> None:
        ret = UnsafeLog.exception(msg, *args, **{'return_only': True, 'frame_level': 3, **kwargs})
        self.__send(("x", (ret, args, kwargs)))

    def close(self) -> None:
        self.__send(('exit',))
        self.__started = False
        if self.__class__.__process:
            self.__class__.__process.get_results()
            self.__class__.__process.close()

    def __send(self, msg: tuple) -> None:
        assert self.__started, "The logger is closed"
        clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientsocket.settimeout(10)
        clientsocket.connect(('localhost', self.__port))
        clientsocket.send((json.dumps(msg) + "\n").encode('UTF-8'))
