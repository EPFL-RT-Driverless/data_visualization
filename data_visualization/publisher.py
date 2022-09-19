#  Copyright (c) 2022. Tudor Oancea, Mattéo Berthet, EPFL Racing Team Driverless
import pickle
import struct
from queue import Queue
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from time import sleep
from typing import Union

import cv2

from .constants import *

__all__ = ["Publisher"]


class Publisher(ErrorMessageMixin):
    """
    Description:
    -----------

    Class used to send data to a Subscriber class that is to be plotted in live dynamic mode.
    It uses a socket connection that is dealt with in an auxiliary thread.

    Usage:
    ------

    >>> publisher = Publisher(host, port)
    >>> publisher.publish_msg("hello")
    >>> publisher.publish_msg({"subplot_1": {"curve_1": np.random.rand(10)}})
    """

    host: str  # Hostname of the machine on which runs the Subscriber.
    port: int  # port to which to connect
    stop: bool  # used to stop the auxiliary thread when the main thread is killed
    _msg_queue: Queue  # queue used to send data to publish to the auxiliary thread
    msg_history: list  # list of all the messages sent
    _publisher_socket: socket  # socket used to connect to the Subscriber
    _publisher_thread: Thread  # thread used to send data to the Subscriber
    verbose: bool  # if True, print the status messages

    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT, **kwargs):
        super().__init__(**kwargs)
        self.host = host
        self.port = port
        self.stop = False
        self._msg_queue = Queue()
        self.msg_history = []

        # connect the socket
        self._publisher_socket = socket(AF_INET, SOCK_STREAM)
        self._publisher_socket.bind((host, port))
        self._publisher_socket.listen(5)

        # start the auxiliary thread
        self._publisher_thread = Thread(
            target=self._publisher_thread_target, args=(self._publisher_socket,)
        )
        self._publisher_thread.start()

    def publish_msg(self, msg: Union[str, dict, tuple]):
        """
        Publish a message to the Subscriber (embedded in a Plot) via the socket to which
         it is connected.

        :param msg: message to be sent, either a string that should only be STOP_SIGNAL
        or a dictionary containing the data to be plotted
        """
        if type(msg) == tuple:
            new_msg = (msg[0], cv2.imencode(".jpeg", msg[1], [60, 90])[1])
        else:
            new_msg = msg

        self.msg_history.append(new_msg)
        self._msg_queue.put(new_msg)
        self._print_status_message(
            "added message to publish queue, new size: {}".format(
                self._msg_queue.qsize()
            )
        )

    def terminate(self):
        self._print_status_message("Terminating...")
        self.stop = True
        # self._print_status_message(self.msg_history)
        self._publisher_thread.join()
        self._print_status_message("Server thread is joined")
        self._publisher_socket.close()
        self._print_status_message("Socket is closed")
        self._print_status_message("off")

    def send_msg(self, client, msg):
        # Prefix each message with a 4-byte length (network byte order)
        msg = struct.pack(">I", len(msg)) + msg
        client.sendall(msg)

    def _publisher_thread_target(self, s):
        self._print_status_message("Server is ready ...")

        s.settimeout(15)
        client, adr = s.accept()

        self._print_status_message("Connection established")
        while True:
            if self.stop:
                self.send_msg(client, pickle.dumps(STOP_SIGNAL))
                self._print_status_message("Switching off...")
                break

            if self._msg_queue.empty():
                sleep(0.1)
            else:
                item = self._msg_queue.get_nowait()
                data = pickle.dumps(item)
                self.send_msg(client, data)
                self._print_status_message("sent")
                self._print_status_message(str(len(data)))
                if item == STOP_SIGNAL:
                    print("Switching off...")
                    break

        client.close()
        self._print_status_message("Connection closed")
