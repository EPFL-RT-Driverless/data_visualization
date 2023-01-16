import numpy as np

from data_visualization import *

np.random.seed(127)


def main():
    plot = Plot(
        mode=PlotMode.DYNAMIC,
        col_nbr=2,
        row_nbr=2,
        figsize=(7, 3),
        sampling_time=0.1,
        interval=50,
        show_car=True,
    )
    N = 100  # number of time steps
    M = 10  # number of prediction steps

    # create data for the map subplot
    x = np.linspace(0, 6 * np.pi, N + M)
    y = 5 * np.sin(x / 3) + np.random.randn(N + M) * 0.1
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
        car_ids=[1],
        car_data_type=CarDataType.TRAJECTORY,
        car_data_names=["trajectory"],
    )

    # create data for the orientation and steering angle subplots
    y = np.sin(np.arange(N + M) / 10) + np.random.randn(N + M) * 0.1
    predictions = np.zeros((N, M))
    for i in range(N):
        predictions[i, :] = y[i : i + M]
    trajectory = y[:N]

    plot.add_subplot(
        subplot_name="orientation",
        row_idx=0,
        col_idx=1,
        subplot_type=SubplotType.TEMPORAL,
        unit="rad",
        show_unit=True,
        curves={
            "orientation": {
                "data": trajectory,
                "curve_type": CurveType.REGULAR,
                "curve_style": CurvePlotStyle.PLOT,
                "mpl_options": {"color": "blue"},
            },
            "orientation_pred": {
                "data": predictions,
                "curve_type": CurveType.PREDICTION,
                "curve_style": CurvePlotStyle.PLOT,
                "mpl_options": {"color": "green"},
            },
        },
        car_ids=[1],
        car_data_type=CarDataType.ORIENTATION,
        car_data_names=["orientation"],
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
        car_ids=[1],
        car_data_type=CarDataType.STEERING,
        car_data_names=["steering"],
    )
    plot.plot(show=True)
    # plot.plot(save_path="car_example.gif")


if __name__ == "__main__":
    main()
