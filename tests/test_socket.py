from data_visualization.subscriber import Subscriber, launch_client
from multiprocessing import Queue
q = Queue()
launch_client(q, verbose=True)
