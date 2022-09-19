import numpy as np

from data_visualization import *

if __name__ == "__main__":
    plot = Plot(
        row_nbr=1,
        col_nbr=2,
        mode=PlotMode.LIVE_DYNAMIC,
        interval=100,
        verbose=False,
    )
    plot.add_subplot(
        subplot_name="temporal",
        col_idx=0,
        row_idx=0,
        unit="rad",
        show_unit=False,
        subplot_type=SubplotType.TEMPORAL,
        curves={
            "yaw_max": {
                "data": np.zeros(5),
                "curve_type": CurveType.STATIC,
                "curve_style": CurvePlotStyle.PLOT,
                "mpl_options": {},
            },
            "yaw": {
                "data": None,
                "curve_style": CurvePlotStyle.PLOT,
                "curve_type": CurveType.REGULAR,
                "mpl_options": {},
            },
            "yaw_pred": {
                "data": None,
                "curve_style": CurvePlotStyle.PLOT,
                "curve_type": CurveType.PREDICTION,
                "mpl_options": {},
            },
        },
    )
    plot.add_subplot(
        subplot_name="spatial",
        col_idx=1,
        row_idx=0,
        unit="m",
        show_unit=False,
        subplot_type=SubplotType.SPATIAL,
        curves={
            "cones": {
                "data": np.array([np.arange(4), np.arange(4)]).T,
                "curve_type": CurveType.STATIC,
                "curve_style": CurvePlotStyle.PLOT,
                "mpl_options": {},
            },
            "traj": {
                "data": None,
                "curve_style": CurvePlotStyle.PLOT,
                "curve_type": CurveType.REGULAR,
                "mpl_options": {},
            },
            "traj_pred": {
                "data": None,
                "curve_style": CurvePlotStyle.PLOT,
                "curve_type": CurveType.PREDICTION,
                "mpl_options": {},
            },
        },
    )
    plot.plot(show=True)
