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
        interval=10,
    )
    N = 100
    M = 10
    # create a sin wave with noise, of length N+M and then extract the predictions at each N time step
    x = np.linspace(0, 2 * np.pi, N + M)
    y = np.sin(x) + np.random.randn(N + M) * 0.1
    predictions = np.zeros((N, M, 2))
    for i in range(N):
        predictions[i, :, 0] = x[i : i + M]
        predictions[i, :, 1] = y[i : i + M]
    trajectory = np.array([x[:N], y[:N]]).T

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
                "data": trajectory,
                "curve_type": CurveType.REGULAR,
                "curve_style": CurvePlotStyle.PLOT,
                "mpl_options": {"color": "blue"},
            },
            "trajectory_pred": {
                "data": predictions,
                "curve_type": CurveType.PREDICTION,
                "curve_style": CurvePlotStyle.PLOT,
                "mpl_options": {"color": "green"},
            },
        },
    )
    # same thing for speed
    y = np.random.rand(N + M) * 10
    predictions = np.zeros((N, M))
    for i in range(N):
        predictions[i, :] = y[i : i + M]
    trajectory = y[:N]

    x = np.sin(np.linspace(0, 2 * np.pi, 100).reshape(10, 10))
    plot.add_subplot(
        subplot_name="speed",
        row_idx=0,
        col_idx=1,
        subplot_type=SubplotType.TEMPORAL,
        unit="m/s",
        show_unit=True,
        curves={
            "speed": {
                "data": trajectory,
                "curve_type": CurveType.REGULAR,
                "curve_style": CurvePlotStyle.PLOT,
                "mpl_options": {"color": "blue"},
            },
            "speed_pred": {
                "data": predictions,
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
                "data": trajectory,
                "curve_type": CurveType.REGULAR,
                "curve_style": CurvePlotStyle.STEP,
                "mpl_options": {"color": "blue"},
            },
            "steering_pred": {
                "data": predictions,
                "curve_type": CurveType.PREDICTION,
                "curve_style": CurvePlotStyle.STEP,
                "mpl_options": {"color": "green"},
            },
        },
    )
    plot.plot(show=True)


if __name__ == "__main__":
    main()
