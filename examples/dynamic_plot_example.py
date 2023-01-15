import numpy as np

from data_visualization import *

np.random.seed(127)


def main():
    plot = Plot(
        mode=PlotMode.DYNAMIC,
        col_nbr=2,
        row_nbr=2,
        figsize=(7, 7),
        sampling_time=0.1,
        interval=500,
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
            "trajectory_pred": {
                "data": np.random.rand(10, 5, 2),
                "curve_type": CurveType.PREDICTION,
                "curve_style": CurvePlotStyle.PLOT,
                "mpl_options": {"color": "green"},
            },
        },
    )
    speed_data = np.random.rand(10)
    speed_prediction = np.concatenate(
        (
            np.array([np.arange(len(speed_data)), speed_data]).T[:, np.newaxis, :],
            np.random.rand(10, 4, 2),
        ),
        axis=1,
    )
    print(speed_data.shape)
    print(speed_prediction.shape)
    plot.add_subplot(
        subplot_name="speed",
        row_idx=0,
        col_idx=1,
        subplot_type=SubplotType.TEMPORAL,
        unit="m/s",
        show_unit=True,
        curves={
            "speed": {
                "data": speed_data,
                "curve_type": CurveType.REGULAR,
                "curve_style": CurvePlotStyle.PLOT,
                "mpl_options": {"color": "blue"},
            },
            "speed_pred": {
                "data": speed_prediction,
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
                "data": np.random.rand(10),
                "curve_type": CurveType.REGULAR,
                "curve_style": CurvePlotStyle.STEP,
                "mpl_options": {"color": "blue"},
            },
            "steering_pred": {
                "data": np.random.rand(10, 5),
                "curve_type": CurveType.PREDICTION,
                "curve_style": CurvePlotStyle.STEP,
                "mpl_options": {"color": "green"},
            },
        },
    )
    plot.plot(show=True)


if __name__ == "__main__":
    main()
