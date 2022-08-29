import pickle
import socket
import numpy as np
from threading import Thread
from time import sleep
import queue
import signal
import sys
import struct

is_killed = False

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 1024  # The port used by the server

class Telemetry:
    def __init__(self):
        self.kill_thread = False
        signal.signal(signal.SIGINT, self.signal_handler)
        self.queue = queue.Queue()
        self.state_history = []
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.s.bind((socket.gethostname(), 1024))
        self.s.bind((HOST, PORT))
        self.s.listen(5)
        self.thread = Thread(target=self.server_thread, args=(self.s,))
        self.thread.start()

    def update(self, data, cones, image):
        # self.queue.put(np.array([data, cones, image], dtype=object))
        # self.queue.put((data, cones, image))
        self.queue.put([data, cones, 0])
        print("updated", self.queue.qsize())

    def signal_handler(self, signal, frame):

        print("You pressed Ctrl+C!")

        self.kill_thread = True

        print(self.state_history)

        self.thread.join()
        print("Server thread is joined")

        self.s.close()
        print("Socket is closed")

        sleep(1)

        print("Off")

    def get_all_queue_result(self):

        result_list = []

        while not self.queue.empty():
            result_list.append(self.queue.get_nowait())

        print(len(result_list))

        return result_list

    def server_thread(self, s):
        print("Server is ready ...")

        s.settimeout(15)
        client, adr = s.accept()

        print("Connection established")
        while True:
            if self.kill_thread:
                print("Switching off...")
                break
            # print(f'Connection to {adr} established')

            if self.queue.empty():
                # print("Queue is empty")
                # client.send(pickle.dumps("empty"))
                sleep(0.1)
            else:
                # client.send(pickle.dumps(self.get_all_queue_result()))
                data = pickle.dumps(self.queue.get_nowait())
                size = len(data)
                #print(data)
                #print("presend")
                #self.s.sendall(struct.pack(">L", size) + data) #'''struct.pack(">L") + '''
                client.sendall(data)
                print("sent")

        client.close()
        print("Connection closed")


if __name__ == "__main__":

    server = Telemetry()
    while True:
        if server.kill_thread:
            break
        array = np.random.rand(1, 5)
        server.state_history.append(array)
        server.queue.put(array)
        sleep(1)
        print("added")
        print(len(server.state_history))
        print(server.queue.qsize())
        # print(self.stack.get())
