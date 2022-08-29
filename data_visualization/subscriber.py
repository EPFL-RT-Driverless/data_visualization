#  Copyright (c) 2022. Tudor Oancea, Mattéo Berthet EPFL Racing Team Driverless
import pickle
import socket
from multiprocessing import Queue
import warnings

__all__ = ["Subscriber", "launch_client"]


class Subscriber:
    host: str
    port: int
    msg_size: int
    q: Queue
    verbose: bool

    s: socket.socket

    def __init__(
        self,
        q: Queue,
        host: str = "127.0.0.1",
        port: int = 1024,
        msg_size: int = 4096,
        verbose: bool = True,
    ):
        self.host = host
        self.port = port
        self.msg_size = msg_size
        self.q = q
        self.verbose = verbose

    def wait_connect(self):
        connected = False
        if self.verbose:
            print("connecting ...")
        while not connected:
            try:
                self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.s.connect((self.host, self.port))
                connected = True
            except:
                pass  # Do nothing, just try again

        if self.verbose:
            print("connected")

    def run(self):
        while True:
            stream = self.s.recv(self.msg_size)
            try:
                data = pickle.loads(stream)
            except:
                data = None
                warnings.warn("pickle error (message size may be too short)")

            self.q.put(data)
            if self.verbose:
                print("added")


def launch_client(
    q: Queue,
    host: str = "127.0.0.1",
    port: int = 1024,
    msg_size: int = 4096,
    verbose: bool = True,
):
    client = Subscriber(q, host, port, msg_size, verbose)
    client.wait_connect()
    client.run()
