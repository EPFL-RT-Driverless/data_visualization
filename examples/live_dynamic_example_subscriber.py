#  Copyright (c) 2022. Tudor Oancea, EPFL Racing Team Driverless
import numpy as np

from data_visualization import *

np.random.seed(127)


def main():
    plot = Plot(
        mode=PlotMode.LIVE_DYNAMIC,
        col_nbr=2,
        row_nbr=2,
        figsize=(7, 3),
        sampling_time=0.1,
        interval=10,
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
                "data": np.random.rand(10, 2) * np.pi,
                "curve_type": CurveType.STATIC,
                "curve_style": CurvePlotStyle.SCATTER,
                "mpl_options": {"color": "red", "marker": "^"},
            },
            "trajectory": {
                "data": None,
                "curve_type": CurveType.REGULAR,
                "curve_style": CurvePlotStyle.PLOT,
                "mpl_options": {"color": "blue"},
            },
            "trajectory_pred": {
                "data": None,
                "curve_type": CurveType.PREDICTION,
                "curve_style": CurvePlotStyle.PLOT,
                "mpl_options": {"color": "green"},
            },
        },
    )
    plot.add_subplot(
        subplot_name="orientation",
        row_idx=0,
        col_idx=1,
        subplot_type=SubplotType.TEMPORAL,
        unit="rad",
        show_unit=True,
        curves={
            "orientation": {
                "data": None,
                "curve_type": CurveType.REGULAR,
                "curve_style": CurvePlotStyle.PLOT,
                "mpl_options": {"color": "blue"},
            },
            "orientation_pred": {
                "data": None,
                "curve_type": CurveType.PREDICTION,
                "curve_style": CurvePlotStyle.PLOT,
                "mpl_options": {"color": "green"},
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
                "data": None,
                "curve_type": CurveType.REGULAR,
                "curve_style": CurvePlotStyle.STEP,
                "mpl_options": {"color": "blue"},
            },
            "steering_pred": {
                "data": None,
                "curve_type": CurveType.PREDICTION,
                "curve_style": CurvePlotStyle.STEP,
                "mpl_options": {"color": "green"},
            },
        },
    )
    plot.plot(show=True)


if __name__ == "__main__":
    main()
