import numpy as np

from data_visualization import *

np.random.seed(127)


def main():
    plot = Plot(
        mode=PlotMode.STATIC,
        col_nbr=2,
        row_nbr=2,
        figsize=(7, 7),
    )
    plot.add_subplot(
        subplot_name="map",
        row_idx=range(2),
        col_idx=0,
        subplot_type=SubplotType.SPATIAL,
        unit="m",
        show_unit=True,
        curves={
            "cones": {
                "data": np.random.rand(10, 2),
                "curve_type": CurveType.STATIC,
                "curve_style": CurvePlotStyle.SCATTER,
                "mpl_options": {"color": "red", "marker": "^"},
            },
            "trajectory": {
                "data": np.random.rand(10, 2),
                "curve_type": CurveType.REGULAR,
                "curve_style": CurvePlotStyle.PLOT,
                "mpl_options": {"color": "blue"},
            },
        },
    )
    plot.add_subplot(
        subplot_name="speed",
        row_idx=0,
        col_idx=1,
        subplot_type=SubplotType.TEMPORAL,
        unit="m/s",
        show_unit=True,
        curves={
            "speed": {
                "data": np.random.rand(10),
                "curve_type": CurveType.REGULAR,
                "curve_style": CurvePlotStyle.PLOT,
                "mpl_options": {"color": "blue"},
            },
        },
    )
    plot.add_subplot(
        subplot_name="steering",
        row_idx=1,
        col_idx=1,
        subplot_type=SubplotType.TEMPORAL,
        unit="rad",
        show_unit=True,
        curves={
            "steering": {
                "data": np.random.rand(10),
                "curve_type": CurveType.REGULAR,
                "curve_style": CurvePlotStyle.PLOT,
                "mpl_options": {"color": "blue"},
            },
        },
    )
    plot.plot(show=True)


if __name__ == "__main__":
    main()
