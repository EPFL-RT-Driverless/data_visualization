import numpy as np
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from track_database import skidpad, acceleration_track
from data_visualization.plot import *
import data_visualization


def main():
    if not len(sys.argv) > 1:
        print("Testing basic plot")
        test_plot()
    else:
        print("Testing telemetry plot")
        track = sys.argv[1]
        if track not in ["skidpad", "acceleration"]:
            print("Invalid track name")
            return

        show_units = False
        if len(sys.argv) > 2:
            show_units = sys.argv[2] == "show_units"
        test_plot_telemetry(track, show_units=show_units)


def test_plot_telemetry(track, show_units=False):
    center_line, _, _, _ = (
        skidpad(0.5) if track == "skidpad" else acceleration_track(0.5)
    )

    data_visualization.plot.plot_telemetry(
        track,
        trajectory=center_line + np.random.normal(0, 0.1, center_line.shape),
        steering=20 * np.sin(2 * np.linspace(0, 2 * np.pi, 100))
        + 60
        + np.random.normal(0, 0.1, 100),
        motor=np.repeat(1400, 100) + np.random.normal(0, 0.1, 100),
        yaw=4 * np.sin(2 * np.linspace(0, 2 * np.pi, 100))
        + np.random.normal(0, 0.1, 100),
        yaw_rate=4 * np.sin(2 * np.linspace(0, 2 * np.pi, 100))
        + np.random.normal(0, 0.1, 100),
        vx=np.concatenate((np.linspace(0, 10, 30), np.repeat(10, 70)))
        + np.random.normal(0, 0.1, 100),
        vy=np.concatenate((np.linspace(0, 10, 30), np.repeat(10, 70)))
        + np.random.normal(0, 0.1, 100),
        show_units=show_units,
    )


def test_plot():
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
                "data": np.random.rand(4, 2) * 10.0,
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


TESTS = {
    "plot": test_plot,
    "telemetry": test_plot_telemetry,
}

if __name__ == "__main__":
    main()
