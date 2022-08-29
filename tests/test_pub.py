import numpy as np
from time import sleep

from data_visualization import Publisher

if __name__ == "__main__":
    server = Publisher()
    while True:
        if server.kill_thread:
            break
        #input("entrez svp")

        # array = np.random.rand(1, 10)
        di = {
            "temporal": {
                "yaw": np.random.rand() * 0.06 - 0.03,
                "yaw_pred": np.random.rand(3) * 0.06 - 0.03,
            },
            "spatial": {
                "traj": np.random.rand(2),
                "traj_pred": np.random.rand(2, 5),
            },
        }

        server.state_history.append(di)
        server.queue.put(di)
        sleep(1)
        print("added")
        print(len(server.state_history))
        print(server.queue.qsize())
        # print(self.stack.get())
