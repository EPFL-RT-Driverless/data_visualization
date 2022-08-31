import numpy as np
from time import perf_counter
from fsds_client import Simulation

from data_visualization import Publisher, STOP_SIGNAL


def sleep_precise(sec):
    start = perf_counter()
    while perf_counter() - start < sec:
        pass


if __name__ == "__main__":
    publisher = Publisher()
    sim = Simulation(ip="10.211.55.3")
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
        sim.update_image()
        publisher.publish_msg((di, sim.get_image()))
        publisher.publish_msg(di)
        sleep_precise(0.05)

    publisher.publish_msg(STOP_SIGNAL)
