import numpy as np
from matplotlib import pyplot as plt

from data_visualization import *

if __name__ == "__main__":
    plot = Plot(
        row_nbr=4,
        col_nbr=2,
        mode=PlotMode.DYNAMIC,
        sampling_time=0.1,
        interval=50,
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
                "data": np.random.rand(2, 4) * 10.0,
                "curve_type": CurveType.STATIC,
                "curve_style": CurvePlotStyle.SCATTER,
                "mpl_options": {"color": "red", "marker": "^"},
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
                "data": np.sin(np.linspace(0, 2 * np.pi, 100)),
                "curve_type": CurveType.REGULAR,
                "curve_style": CurvePlotStyle.PLOT,
                "options": {"color": "blue", "marker": "o"},
            },
        },
    )
    plot.plot(show=True)
