import numpy as np
import signal
from time import perf_counter
from fsds_client import Simulation

from data_visualization import Publisher, STOP_SIGNAL


def sleep_precise(sec):
    start = perf_counter()
    while perf_counter() - start < sec:
        pass


def signal_handler(publisher):
    print("You pressed Ctrl+C!")
    publisher.terminate()
    exit(0)


if __name__ == "__main__":
    publisher = Publisher(verbose=True)

    def bruh(s, b):
        signal_handler(publisher)

    signal.signal(signal.SIGINT, bruh)
    sim = Simulation(ip="10.211.55.3")
    for i in range(300):
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
        if i % 5 == 0:
            sim.update_image()
            publisher.publish_msg((di, sim.get_image()))
        else:
            publisher.publish_msg(di)
        # publisher.publish_msg(di)

        sleep_precise(0.1)

    publisher.publish_msg(STOP_SIGNAL)
