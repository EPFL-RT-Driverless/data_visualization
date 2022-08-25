import numpy as np
from matplotlib import pyplot as plt

from data_visualization import *

if __name__ == "__main__":
    plot = Plot(
        row_nbr=4,
        col_nbr=2,
        mode=PlotMode.STATIC,
    )
    plot.add_subplot(
        subplot_name="map",
        row_idx=range(4),
        col_idx=0,
        unit="m",
        show_unit=True,
        subplot_type=SubplotType.SPATIAL,
        curves={
            "left_cones": {
                "data": np.zeros((2, 10)),
                "curve_type": CurveType.REGULAR,
                "curve_style": CurvePlotStyle.PLOT,
                "mpl_options": {"color": "red", "marker": "o"},
            },
        },
    )
    plot.add_subplot(
        subplot_name="yaw",
        row_idx=1,
        col_idx=1,
        unit="rad",
        show_unit=True,
        subplot_type=SubplotType.TEMPORAL,
        curves={
            "yaw": {
                "data": np.zeros((2, 10)),
                "curve_type": CurveType.REGULAR,
                "curve_style": CurvePlotStyle.PLOT,
                "options": {"color": "blue", "marker": "o"},
            },
        },
    )
    plt.show()
