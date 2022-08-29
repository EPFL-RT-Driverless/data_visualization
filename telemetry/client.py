import socket
import numpy as np
import pickle
from time import sleep
import matplotlib.pyplot as plt

liste = []

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 1024  # The port used by the server

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#s.connect((socket.gethostname(), 1024))
s.connect((HOST, PORT))
#s.bind((socket.gethostname(), 1024))
while True:
    print("test")
    stream = s.recv(1024)
    #stream = s.recv(1671168)
    print("testbis")
    #if not stream:
    #    break
    #print("test2")
    data = pickle.loads(stream)
    print("ok")
    if data == []:
        print("Queue is empty")
    else:
        # print(data)
        liste.extend(data)
        print("added")
    print(len(liste))
    #plt.plot(np.array(liste).T)
    #plt.show()
    print(pickle.loads(stream))
    #save_send_telemetry(data[0])
s.close()
print(liste)
