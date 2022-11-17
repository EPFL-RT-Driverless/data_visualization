import numpy as np
import pytest

from data_visualization import *

def test_same_name():
    with pytest.raises(ValueError,match="A subplot with the same name already exists"):
        plot = Plot(
            mode=PlotMode.STATIC,
            sampling_time=0.1,
            interval=50,
            row_nbr=1,
            col_nbr=1,
        )
        plot.add_subplot(
            subplot_name="test spatial plot step: ",
            subplot_type=SubplotType.SPATIAL,
            row_idx=0,
            col_idx=0,
            unit="unit",
            show_unit=True,
            curves={
                "x": {
                    "data": (np.random.rand(20, 2) * 10.0),
                    "curve_type": CurveType.STATIC,
                    "curve_style": CurvePlotStyle.STEP,
                    "mpl_options": {"color": "red", "marker": "^"}
                },
                "y": {
                    "data": (np.random.rand(20, 2) * 10.0),
                    "curve_type": CurveType.REGULAR,
                    "curve_style": CurvePlotStyle.STEP,
                    "mpl_options": {"color": "blue"}
                },
            }
        )
        plot.add_subplot(
            subplot_name="test spatial plot step: ",
            subplot_type=SubplotType.SPATIAL,
            row_idx=0,
            col_idx=0,
            unit="unit",
            show_unit=True,
            curves={
                "x": {
                    "data": (np.random.rand(20, 2) * 10.0),
                    "curve_type": CurveType.STATIC,
                    "curve_style": CurvePlotStyle.STEP,
                    "mpl_options": {"color": "red", "marker": "^"}
                },
                "y": {
                    "data": (np.random.rand(20, 2) * 10.0),
                    "curve_type": CurveType.REGULAR,
                    "curve_style": CurvePlotStyle.STEP,
                    "mpl_options": {"color": "blue"}
                },
            }
        )

def test_superpose():
    with pytest.raises(ValueError,match="The subplot superposes with other subplots"):
        plot = Plot(
            mode=PlotMode.STATIC,
            sampling_time=0.1,
            interval=50,
            row_nbr=1,
            col_nbr=1,
        )
        plot.add_subplot(
            subplot_name="test spatial plot step: ",
            subplot_type=SubplotType.SPATIAL,
            row_idx=0,
            col_idx=0,
            unit="unit",
            show_unit=True,
            curves={
                "x": {
                    "data": (np.random.rand(20, 2) * 10.0),
                    "curve_type": CurveType.STATIC,
                    "curve_style": CurvePlotStyle.STEP,
                    "mpl_options": {"color": "red", "marker": "^"}
                },
                "y": {
                    "data": (np.random.rand(20, 2) * 10.0),
                    "curve_type": CurveType.REGULAR,
                    "curve_style": CurvePlotStyle.STEP,
                    "mpl_options": {"color": "blue"}
                },
            }
        )
        plot.add_subplot(
            subplot_name="test spatial plot step: 2",
            subplot_type=SubplotType.SPATIAL,
            row_idx=0,
            col_idx=0,
            unit="unit",
            show_unit=True,
            curves={
                "x": {
                    "data": (np.random.rand(20, 2) * 10.0),
                    "curve_type": CurveType.STATIC,
                    "curve_style": CurvePlotStyle.STEP,
                    "mpl_options": {"color": "red", "marker": "^"}
                },
                "y": {
                    "data": (np.random.rand(20, 2) * 10.0),
                    "curve_type": CurveType.REGULAR,
                    "curve_style": CurvePlotStyle.STEP,
                    "mpl_options": {"color": "blue"}
                },
            }
        )


@pytest.mark.parametrize("mode,mode_name", [(PlotMode.STATIC, "STATIC"), (PlotMode.DYNAMIC, "DYNAMIC")])
def test_spatial_plot_scatter(mode: int, mode_name: str):
    plot = Plot(
        mode=mode,
        sampling_time=0.1,
        interval=50,
        row_nbr=1,
        col_nbr=1,
    )
    plot.add_subplot(
        subplot_name="test spatial plot scatter: " + mode_name,
        subplot_type=SubplotType.SPATIAL,
        row_idx=0,
        col_idx=0,
        unit="unit",
        show_unit=True,
        curves={
            "x": {
                "data": (np.random.rand(20, 2) * 10.0),
                "curve_type": CurveType.STATIC,
                "curve_style": CurvePlotStyle.SCATTER,
                "mpl_options": {"color": "red", "marker": "^"}
            },
            # [NOTE] Dynamic scatter is not implemented yet
            "y": {
                "data": np.array([[1, 2],
                                  [1, 3],
                                  [1, 4],
                                  [1, 5],
                                  [1, 6],
                                  [3, 6],
                                  [4, 6],
                                  [5, 6],
                                  [5, 5],
                                  [5, 4],
                                  [4, 4],
                                  [3, 4],
                                  [3, 3],
                                  [3, 2],
                                  [4, 2],
                                  [5, 2],
                                  [7, 6],
                                  [8, 6],
                                  [9, 6],
                                  [9, 5],
                                  [9, 4],
                                  [8, 3],
                                  [7, 2]]),
                "curve_type": CurveType.REGULAR,
                "curve_style": CurvePlotStyle.PLOT,
                "mpl_options": {"color": "blue", "marker": "o"}
            },
        }
    )
    plot.plot(show=True)

@pytest.mark.parametrize("mode,mode_name", [(PlotMode.STATIC, "STATIC"), (PlotMode.DYNAMIC, "DYNAMIC")])
def test_spatial_plot_plot(mode: int, mode_name: str):
    plot = Plot(
        mode=mode,
        sampling_time=0.1,
        interval=50,
        row_nbr=1,
        col_nbr=1,
    )
    plot.add_subplot(
        subplot_name="test spatial plot plot: " + mode_name,
        subplot_type=SubplotType.SPATIAL,
        row_idx=0,
        col_idx=0,
        unit="unit",
        show_unit=True,
        curves={
            "x": {
                "data": (np.random.rand(20, 2) * 10.0),
                "curve_type": CurveType.STATIC,
                "curve_style": CurvePlotStyle.PLOT,
                "mpl_options": {"color": "red", "marker": "^"}
            },
            "y": {
                "data": np.array([[1, 2],
                                  [1, 3],
                                  [1, 4],
                                  [1, 5],
                                  [1, 6],
                                  [3, 6],
                                  [4, 6],
                                  [5, 6],
                                  [5, 5],
                                  [5, 4],
                                  [4, 4],
                                  [3, 4],
                                  [3, 3],
                                  [3, 2],
                                  [4, 2],
                                  [5, 2],
                                  [7, 6],
                                  [8, 6],
                                  [9, 6],
                                  [9, 5],
                                  [9, 4],
                                  [8, 3],
                                  [7, 2]]),
                "curve_type": CurveType.REGULAR,
                "curve_style": CurvePlotStyle.PLOT,
                "mpl_options": {"color": "blue"}
            },
        }
    )
    plot.plot(show=True)

@pytest.mark.parametrize("mode,mode_name", [(PlotMode.STATIC, "STATIC"), (PlotMode.DYNAMIC, "DYNAMIC")])
def test_spatial_plot_step(mode: int, mode_name: str):
    plot = Plot(
        mode=mode,
        sampling_time=0.1,
        interval=50,
        row_nbr=1,
        col_nbr=1,
    )
    plot.add_subplot(
        subplot_name="test spatial plot step: " + mode_name,
        subplot_type=SubplotType.SPATIAL,
        row_idx=0,
        col_idx=0,
        unit="unit",
        show_unit=True,
        curves={
            "x": {
                "data": (np.random.rand(20, 2) * 10.0),
                "curve_type": CurveType.STATIC,
                "curve_style": CurvePlotStyle.STEP,
                "mpl_options": {"color": "red", "marker": "^"}
            },
            "y": {
                "data": (np.random.rand(20, 2) * 10.0),
                "curve_type": CurveType.REGULAR,
                "curve_style": CurvePlotStyle.STEP,
                "mpl_options": {"color": "blue"}
            },
        }
    )
    plot.plot(show=True)

@pytest.mark.parametrize("mode,mode_name", [(PlotMode.STATIC, "STATIC")])
def test_temporal_plot_scatter(mode: int, mode_name: str):
    plot = Plot(
        mode=mode,
        sampling_time=0.1,
        interval=10,
        row_nbr=1,
        col_nbr=1,
    )
    plot.add_subplot(
        subplot_name="test temporal plot scatter: " + mode_name,
        subplot_type=SubplotType.TEMPORAL,
        row_idx=0,
        col_idx=0,
        unit="unit",
        show_unit=True,
        curves={
            "yaw": {
                "data": np.sin(np.linspace(0, 2 * np.pi, 100)),
                "curve_type": CurveType.STATIC,
                "curve_style": CurvePlotStyle.SCATTER,
                "options": {"color": "blue", "marker": "o"},
            },
        }
    )
    plot.plot(show=True)

@pytest.mark.parametrize("mode,mode_name", [(PlotMode.STATIC, "STATIC"), (PlotMode.DYNAMIC, "DYNAMIC")])
def test_temporal_plot_plot(mode: int, mode_name: str):
    plot = Plot(
        mode=mode,
        sampling_time=0.1,
        interval=10,
        row_nbr=1,
        col_nbr=1,
    )
    plot.add_subplot(
        subplot_name="test temporal plot plot: " + mode_name,
        subplot_type=SubplotType.TEMPORAL,
        row_idx=0,
        col_idx=0,
        unit="unit",
        show_unit=True,
        curves={
            "yaw": {
                "data": np.sin(np.linspace(0, 2 * np.pi, 100)),
                "curve_type": CurveType.REGULAR,
                "curve_style": CurvePlotStyle.PLOT,
                "options": {"color": "blue", "marker": "o"},
            },
        }
    )
    plot.plot(show=True)

@pytest.mark.parametrize("mode,mode_name", [(PlotMode.STATIC, "STATIC"), (PlotMode.DYNAMIC, "DYNAMIC")])
def test_temporal_plot_step(mode: int, mode_name: str):
    plot = Plot(
        mode=mode,
        sampling_time=0.1,
        interval=10,
        row_nbr=1,
        col_nbr=1,
    )
    plot.add_subplot(
        subplot_name="test temporal plot step: " + mode_name,
        subplot_type=SubplotType.TEMPORAL,
        row_idx=0,
        col_idx=0,
        unit="unit",
        show_unit=True,
        curves={
            "yaw": {
                "data": np.sin(np.linspace(0, 2 * np.pi, 100)),
                "curve_type": CurveType.REGULAR,
                "curve_style": CurvePlotStyle.STEP,
                "options": {"color": "blue", "marker": "o"},
            },
        }
    )
    plot.plot(show=True)

@pytest.mark.parametrize("mode,mode_name", [(PlotMode.STATIC, "STATIC"), (PlotMode.DYNAMIC, "DYNAMIC")])
def test_temporal_plot_semilogx(mode: int, mode_name: str):
    plot = Plot(
        mode=mode,
        sampling_time=1.0,
        interval=1,
        row_nbr=1,
        col_nbr=1,
    )
    plot.add_subplot(
        subplot_name="test temporal plot semilogx: " + mode_name,
        subplot_type=SubplotType.TEMPORAL,
        row_idx=0,
        col_idx=0,
        unit="unit",
        show_unit=True,
        curves={
            "yaw": {
                "data": np.logspace(0, 2, 100),
                "curve_type": CurveType.REGULAR,
                "curve_style": CurvePlotStyle.SEMILOGX,
                "options": {"color": "blue", "marker": "o"},
            },
        }
    )
    plot.plot(show=True)

@pytest.mark.parametrize("mode,mode_name", [(PlotMode.STATIC, "STATIC"), (PlotMode.DYNAMIC, "DYNAMIC")])
def test_temporal_plot_semilogy(mode: int, mode_name: str):
    plot = Plot(
        mode=mode,
        sampling_time=1.0,
        interval=1,
        row_nbr=1,
        col_nbr=1,
    )
    plot.add_subplot(
        subplot_name="test temporal plot semilogy: " + mode_name,
        subplot_type=SubplotType.TEMPORAL,
        row_idx=0,
        col_idx=0,
        unit="unit",
        show_unit=True,
        curves={
            "yaw": {
                "data": np.logspace(0, 2, 100),
                "curve_type": CurveType.REGULAR,
                "curve_style": CurvePlotStyle.SEMILOGY,
                "options": {"color": "blue", "marker": "o"},
            },
        }
    )
    plot.plot(show=True)

@pytest.mark.parametrize("mode,mode_name", [(PlotMode.STATIC, "STATIC"), (PlotMode.DYNAMIC, "DYNAMIC")])
def test_temporal_plot_loglog(mode: int, mode_name: str):
    plot = Plot(
        mode=mode,
        sampling_time=1.0,
        interval=1,
        row_nbr=1,
        col_nbr=1,
    )
    plot.add_subplot(
        subplot_name="test temporal plot loglog: " + mode_name,
        subplot_type=SubplotType.TEMPORAL,
        row_idx=0,
        col_idx=0,
        unit="unit",
        show_unit=True,
        curves={
            "yaw": {
                "data": np.logspace(0, 2, 100),
                "curve_type": CurveType.REGULAR,
                "curve_style": CurvePlotStyle.LOGLOG,
                "options": {"color": "blue", "marker": "o"},
            },
        }
    )
    plot.plot(show=True)

def test_temporal_prediction():
    plot = Plot(
        mode=PlotMode.DYNAMIC,
        sampling_time=0.1,
        interval=10,
        row_nbr=1,
        col_nbr=1,
    )
    plot.add_subplot(
        subplot_name="test prediction",
        subplot_type=SubplotType.TEMPORAL,
        row_idx=0,
        col_idx=0,
        unit="unit",
        show_unit=True,
        curves={
            "yaw": {
                "data": np.sin(np.linspace(0, 10 * np.pi, 1000).reshape(100, 10)),
                "curve_type": CurveType.PREDICTION,
                "curve_style": CurvePlotStyle.PLOT,
                "options": {"color": "blue", "marker": "o"},
            },
            "yaw2": {
                "data": np.cos(np.linspace(0, 10 * np.pi, 1000)),
                "curve_type": CurveType.STATIC,
                "curve_style": CurvePlotStyle.PLOT,
                "options": {"color": "red", "marker": "o"},
            },
        }
    )
    # plot.plot(show=True, save_path="test_prediction.mp4")
    plot.plot(show=True)

def test_spatial_prediction():
    plot = Plot(
        mode=PlotMode.DYNAMIC,
        sampling_time=0.1,
        interval=10,
        row_nbr=1,
        col_nbr=1,
    )
    plot.add_subplot(
        subplot_name="test prediction",
        subplot_type=SubplotType.SPATIAL,
        row_idx=0,
        col_idx=0,
        unit="unit",
        show_unit=True,
        curves={
            "yaw": {
                "data": np.array([np.linspace(0, 10 * np.pi, 1000).reshape(100, 10), np.sin(np.linspace(0, 10 * np.pi, 1000).reshape(100, 10))]).transpose(1, 2, 0),
                "curve_type": CurveType.PREDICTION,
                "curve_style": CurvePlotStyle.PLOT,
                "options": {"color": "blue", "marker": "o"},
            },
            "yaw2": {
                "data": np.array([np.linspace(0, 10 * np.pi, 1000), np.cos(np.linspace(0, 10 * np.pi, 1000))]).T,
                "curve_type": CurveType.STATIC,
                "curve_style": CurvePlotStyle.PLOT,
                "options": {"color": "red", "marker": "o"},
            },
        }
    )
    # plot.plot(show=True, save_path="test_prediction.mp4")
    plot.plot(show=True)

@pytest.mark.skip("to be used for visual tests")
def test_all():
    """
    you should see a 2d plot :
        - randomly distributed red triangles
        - randomly distributed blue circles with a line connecting them
    """
    test_spatial_plot_scatter(PlotMode.STATIC, "STATIC")

    """
    you should see a 2d plot :
        - randomly distributed STATIC red triangles
        - 127 written with DYNAMIC blue circles with a line connecting them
    [NOTE] Dynamic scatter is not implemented yet
    """
    test_spatial_plot_scatter(PlotMode.DYNAMIC, "DYNAMIC")

    """
    you should see a 2d plot :
        - randomly distributed red triangles with a line connecting them 
        - 127 written with lines
    """
    test_spatial_plot_plot(PlotMode.STATIC, "STATIC")

    """
    you should see a 2d plot :
        - randomly distributed STATIC red triangles with a line connecting them
        - 127 written with DYNAMIC lines
    """
    test_spatial_plot_plot(PlotMode.DYNAMIC, "DYNAMIC")

    """
    you should see a 2d plot :
        - randomly distributed red triangles with a only vertical or horizontal lines connecting them
        - randomly distributed vecrtical and horizontal lines
    """
    test_spatial_plot_step(PlotMode.STATIC, "STATIC")

    """
    you should see a 2d plot :
        - randomly distributed STATIC red triangles with a only vertical or horizontal lines connecting them
        - randomly distributed DYNAMIC vertical and horizontal lines
    """
    test_spatial_plot_step(PlotMode.DYNAMIC, "DYNAMIC")

if __name__ == "__main__":
    test_spatial_prediction()
    # plot = Plot(
    #     row_nbr=4,
    #     col_nbr=2,
    #     mode=PlotMode.DYNAMIC,
    #     sampling_time=0.1,
    #     interval=50,
    # )
    # plot.add_subplot(
    #     subplot_name="map",
    #     row_idx=range(4),
    #     col_idx=0,
    #     unit="m",
    #     show_unit=True,
    #     subplot_type=SubplotType.SPATIAL,
    #     curves={
    #         "left_cones": {
    #             "data": (np.random.rand(2, 4) * 10.0).T,
    #             "curve_type": CurveType.STATIC,
    #             "curve_style": CurvePlotStyle.SCATTER,
    #             "mpl_options": {"color": "red", "marker": "^"},
    #         },
    #     },
    # )
    # plot.add_subplot(
    #     subplot_name="yaw",
    #     row_idx=1,
    #     col_idx=1,
    #     unit="rad",
    #     show_unit=True,
    #     subplot_type=SubplotType.TEMPORAL,
    #     curves={
    #         "yaw": {
    #             "data": np.sin(np.linspace(0, 2 * np.pi, 100)),
    #             "curve_type": CurveType.REGULAR,
    #             "curve_style": CurvePlotStyle.PLOT,
    #             "options": {"color": "blue", "marker": "o"},
    #         },
    #     },
    # )
    # plot.plot(show=True)
