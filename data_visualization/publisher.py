#  Copyright (c) 2022. Tudor Oancea, Mattéo Berthet EPFL Racing Team Driverless
import pickle
import signal
from queue import Queue
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from time import sleep

from typing import Union
from .constants import DEFAULT_HOST, DEFAULT_PORT

__all__ = ["Publisher"]


class Publisher:
    """
    Class used to send data to a Subscriber class that is to be plotted in live dynamic mode.
    It uses a socket connection that is dealt with in an auxiliary thread.
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
        self.host = host
        self.port = port
        self.stop = False
        self._msg_queue = Queue()
        self.msg_history = []

        self.verbose = False
        for possible_kw in ["debug", "verbose"]:
            if possible_kw in kwargs:
                self.verbose = True
                break

        # connect SIGINT (signal sent when pressing ctrl+C or when killing the program) to stop the auxiliary thread and properly close the socket
        signal.signal(signal.SIGINT, self._signal_handler)

        # connect the socket
        self._publisher_socket = socket(AF_INET, SOCK_STREAM)
        self._publisher_socket.bind((host, port))
        self._publisher_socket.listen(5)

        # start the auxiliary thread
        self._publisher_thread = Thread(
            target=self._publisher_thread_target, args=(self._publisher_socket,)
        )
        self._publisher_thread.start()

    def _print_status_message(self, msg):
        if self.verbose:
            print("[PUBLISHER] : " + msg)

    def publish_msg(self, msg: Union[str, dict]):
        self.msg_history.append(msg)
        self._msg_queue.put(msg)
        self._print_status_message(
            "added message to publish queue, new size: {}".format(
                self._msg_queue.qsize()
            )
        )

    def _signal_handler(self, si, frame):
        self._print_status_message("You pressed Ctrl+C!")
        self.stop = True
        self._print_status_message(self.msg_history)
        self._publisher_thread.join()
        self._print_status_message("Server thread is joined")
        self._publisher_socket.close()
        self._print_status_message("Socket is closed")
        sleep(1)
        self._print_status_message("off")

    # def get_all_queue_result(self):
    #     result_list = []
    #     while not self.queue.empty():
    #         result_list.append(self.queue.get_nowait())
    #
    #     print(len(result_list))
    #     return result_list

    def _publisher_thread_target(self, s):
        self._print_status_message("Server is ready ...")

        s.settimeout(15)
        client, adr = s.accept()

        self._print_status_message("Connection established")
        while True:
            if self.stop:
                self._print_status_message("Switching off...")
                break
                # self._print_status_message()(f'Connection to {adr} established')

            if self._msg_queue.empty():
                # self._print_status_message()("Queue is empty")
                # client.send(pickle.dumps("empty"))
                sleep(0.1)
            else:
                # client.send(pickle.dumps(self.get_all_queue_result()))
                data = pickle.dumps(self._msg_queue.get_nowait())
                # size = len(data)
                # self._print_status_message()(data)
                # self._print_status_message()("presend")
                # self.s.sendall(struct.pack(">L", size) + data) #'''struct.pack(">L") + '''
                client.sendall(data)
                self._print_status_message("sent")

        client.close()
        self._print_status_message("Connection closed")
