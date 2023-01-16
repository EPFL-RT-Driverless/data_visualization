#  Copyright (c) 2022. Tudor Oancea, EPFL Racing Team Driverless
import signal
from time import perf_counter

import numpy as np

from data_visualization import Publisher, STOP_SIGNAL


def sleep_precise(sec):
    start = perf_counter()
    while perf_counter() - start < sec:
        pass


def signal_handler(publisher):
    print("You pressed Ctrl+C!")
    publisher.terminate()
    exit(0)


def main():
    publisher = Publisher(verbose=False)
    # connect SIGINT signal to the signal handler to safely terminate the Publisher's connection
    signal.signal(signal.SIGINT, lambda s, b: signal_handler(publisher))

    N = 100  # number of time steps
    M = 10  # number of prediction steps

    # create data for the map subplot
    x = np.linspace(0, 6 * np.pi, N + M)
    y = 5 * np.sin(x / 3) + np.random.randn(N + M) * 0.1
    traj_pred = np.zeros((N, M, 2))
    for i in range(N):
        traj_pred[i, :, 0] = x[i : i + M]
        traj_pred[i, :, 1] = y[i : i + M]
    traj = np.array([x[:N], y[:N]]).T

    # create data for the speed and steering angle subplots
    y = np.sin(np.arange(N + M) / 10) + np.random.randn(N + M) * 0.1
    orientation_steering_pred = np.zeros((N, M))
    for i in range(N):
        orientation_steering_pred[i, :] = y[i : i + M]
    orientation_steering = y[:N]

    for i in range(N):
        publisher.publish_msg(
            {
                "map": {
                    "trajectory": traj[i],
                    "trajectory_pred": traj_pred[i],
                },
                "orientation": {
                    "orientation": orientation_steering[i],
                    "orientation_pred": orientation_steering_pred[i],
                },
                "steering": {
                    "steering": orientation_steering[i],
                    "steering_pred": orientation_steering_pred[i],
                },
            }
        )
        sleep_precise(0.1)

    publisher.publish_msg(STOP_SIGNAL)


if __name__ == "__main__":
    main()
