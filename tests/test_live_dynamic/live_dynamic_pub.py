import signal
from time import perf_counter

import numpy as np

from data_visualization import Publisher, STOP_SIGNAL
from fsds_client import Simulation


def sleep_precise(sec):
    start = perf_counter()
    while perf_counter() - start < sec:
        pass


def signal_handler(publisher):
    print("You pressed Ctrl+C!")
    publisher.terminate()
    exit(0)


def main(with_sim: bool = False):
    publisher = Publisher(verbose=False)

    def bruh(s, b):
        signal_handler(publisher)

    signal.signal(signal.SIGINT, bruh)
    if with_sim:
        sim = Simulation(ip="10.211.55.3")
        pass
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
        if with_sim:
            if i % 5 == 0:
                sim.update_image()
                publisher.publish_msg((di, sim.get_image()))
            else:
                publisher.publish_msg(di)
        else:
            publisher.publish_msg(di)

        sleep_precise(0.1)

    publisher.publish_msg(STOP_SIGNAL)


if __name__ == "__main__":
    main(False)
