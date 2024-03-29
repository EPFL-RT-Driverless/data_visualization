#  Copyright (c) 2022. Tudor Oancea, Mattéo Berthet EPFL Racing Team Driverless
import pickle
import struct
from multiprocessing import Queue
from socket import socket, AF_INET, SOCK_STREAM

from .constants import *
from .constants import ErrorMessageMixin

__all__ = ["Subscriber", "launch_client"]


class Subscriber(ErrorMessageMixin):
    host: str
    port: int
    msg_size: int
    _msg_queue: Queue
    _subscriber_socket: socket

    def __init__(
        self,
        q: Queue,
        host: str = DEFAULT_HOST,
        port: int = DEFAULT_PORT,
        msg_size: int = 4096,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.host = host
        self.port = port
        self._msg_queue = q
        self.msg_size = msg_size

        # connect to the socket
        connected = False
        self._print_status_message("connecting ...")
        while not connected:
            try:
                self._subscriber_socket = socket(AF_INET, SOCK_STREAM)
                self._subscriber_socket.connect((self.host, self.port))
                connected = True
            except OSError:
                # Do nothing, just try again
                pass

        self._print_status_message("connected !")

    def recv_msg(self):
        # Read message length and unpack it into an integer
        raw_msglen = self.recvall(4)
        if not raw_msglen:
            return None
        msglen = struct.unpack(">I", raw_msglen)[0]
        # Read the message data
        return self.recvall(msglen)

    def recvall(self, n):
        # Helper function to recv n bytes or return None if EOF is hit
        data = bytearray()
        while len(data) < n:
            packet = self._subscriber_socket.recv(n - len(data))
            if not packet:
                return None
            data.extend(packet)
        return data

    def run(self):
        while True:
            stream = self.recv_msg()
            try:
                data = pickle.loads(stream)
            except pickle.PickleError:
                data = None
                self._print_status_message(
                    "pickle error (message size may be too short)"
                )

            if data == STOP_SIGNAL:
                self._print_status_message("Switching off...")
                self._msg_queue.put(STOP_SIGNAL)
                self._subscriber_socket.close()
                break
            self._msg_queue.put(data)
            self._print_status_message("received message and added it to queue")


def launch_client(
    q: Queue,
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    msg_size: int = 2 << 10,
    **kwargs,
):
    client = Subscriber(q, host, port, msg_size, **kwargs)
    client.run()
