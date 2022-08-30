import numpy as np
from time import sleep

from data_visualization import Publisher, STOP_SIGNAL

if __name__ == "__main__":
    publisher = Publisher()
    for i in range(100):
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

        publisher.publish_msg(di)
        sleep(0.1)

    publisher.publish_msg(STOP_SIGNAL)
