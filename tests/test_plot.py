import numpy as np
from matplotlib import pyplot as plt

from data_visualization.plot import Plot

if __name__ == "__main__":
    plot = Plot(4, 1, Plot.Mode.STATIC)
    plot.add_subplot(
        name="map",
        row_idx=slice(4),
        col_idx=slice(1),
        unit="m",
        show_unit=True,
        subplot_type=Plot.SubplotType.SPATIAL,
        curves={
            "left_cones": {
                "data": np.zeros((2, 10)),
                "options": {"color": "red", "marker": "o"},
            },
        },
    )
    plt.show()
