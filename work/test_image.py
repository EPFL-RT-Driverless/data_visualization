from fsds_client import Simulation
import cv2
from time import perf_counter


def sleep(seconds):
    start = perf_counter()
    while perf_counter() - start < seconds:
        pass


if __name__ == "__main__":
    # initialize simulation
    sim = Simulation(ip="10.211.55.3")
    while True:
        # update image
        sim.update_image()
        # get image
        image = sim.get_image()
        # show image
        cv2.imshow("image", image)
        # wait for key
        cv2.waitKey(1)
        # sleep
        sleep(0.1)
