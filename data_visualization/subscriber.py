#  Copyright (c) 2022. Tudor Oancea, Mattéo Berthet EPFL Racing Team Driverless
import pickle
from socket import socket, AF_INET, SOCK_STREAM
from multiprocessing import Queue
import warnings

from .constants import DEFAULT_HOST, DEFAULT_PORT

__all__ = ["Subscriber", "launch_client"]


class Subscriber:
    host: str
    port: int
    msg_size: int
    _msg_queue: Queue
    _subscriber_socket: socket
    verbose: bool

    def __init__(
        self,
        q: Queue,
        host: str = DEFAULT_HOST,
        port: int = DEFAULT_PORT,
        msg_size: int = 4096,
        **kwargs,
    ):
        self.host = host
        self.port = port
        self._msg_queue = q
        self.msg_size = msg_size

        self.verbose = False
        for possible_kw in ["debug", "verbose"]:
            if possible_kw in kwargs:
                self.verbose = True
                break

        # connect to the socket
        connected = False
        self._print_status_message("connecting ...")
        while not connected:
            try:
                self._subscriber_socket = socket(AF_INET, SOCK_STREAM)
                self._subscriber_socket.connect((self.host, self.port))
                connected = True
            except:
                # Do nothing, just try again
                pass

        self._print_status_message("connected !")

    def _print_status_message(self, msg):
        if self.verbose:
            print("[SUBSCRIBER] : " + msg)

    def run(self):
        while True:
            stream = self._subscriber_socket.recv(self.msg_size)
            try:
                data = pickle.loads(stream)
            except:
                data = None
                warnings.warn("pickle error (message size may be too short)")

            self._msg_queue.put(data)
            self._print_status_message("received message and added it to queue")


def launch_client(
    q: Queue,
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    msg_size: int = 4096,
    **kwargs,
):
    client = Subscriber(q, host, port, msg_size, **kwargs)
    client.run()
