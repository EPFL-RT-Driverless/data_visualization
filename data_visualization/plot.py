#  Copyright (c) 2022. Tudor Oancea, Mattéo Berthet, EPFL Racing Team Driverless
import multiprocessing as mp
import warnings
from enum import Enum
from typing import Optional, Union

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.figure import Figure
from matplotlib.gridspec import GridSpec

from .subscriber import launch_client
from .constants import STOP_SIGNAL

__all__ = ["Plot", "PlotMode", "SubplotType", "CurveType", "CurvePlotStyle"]


class PlotMode(Enum):
    STATIC = 0
    DYNAMIC = 1
    LIVE_DYNAMIC = 2


class SubplotType(Enum):
    SPATIAL = 0
    TEMPORAL = 1


class CurveType(Enum):
    STATIC = 0
    REGULAR = 1
    PREDICTION = 2


class CurvePlotStyle(Enum):
    PLOT = 0
    SCATTER = 1
    STEP = 2
    SEMILOGX = 3
    SEMILOGY = 4
    LOGLOG = 5


class Plot:
    """
    # TODO: add docstring
    """

    mode: PlotMode
    _row_nbr: int
    _col_nbr: int
    _interval: Optional[int]
    _sampling_time: Optional[float]

    _fig: Figure
    _gridspec: GridSpec
    _plot_positions: np.ndarray  # np.array of bools
    _content: dict
    _anim: Optional[FuncAnimation]
    _length_curves: int

    # stuff for Live dynamic mode
    _live_dynamic_data_queue: Optional[mp.Queue]
    _no_more_values: Optional[bool]

    def __init__(
        self,
        mode: PlotMode,
        row_nbr: int,
        col_nbr: int,
        interval: Optional[int] = None,
        sampling_time: Optional[float] = None,
        host: str = "127.0.0.1",
        port: int = 1024,
    ):
        """
        Initializes the plot with an empty Gridspec of size row_nbr x col_nbr.

        :param mode: the mode of the plot. Can be STATIC, DYNAMIC, or LIVE_DYNAMIC
        :param row_nbr: number of rows
        :param col_nbr: number of columns
        :param interval: interval between frames in milliseconds, only needed for DYNAMIC and LIVE_DYNAMIC
        :param sampling_time: sampling time used in the experiment, only needed if the temporal subplots need to have an x axis with time instead of number of iteration
        """
        self.mode = mode
        self._row_nbr = row_nbr
        self._col_nbr = col_nbr
        self._interval = interval
        self._sampling_time = sampling_time

        self._fig = plt.figure()
        self._gridspec = self._fig.add_gridspec(row_nbr, col_nbr)
        self._plot_positions = np.zeros((row_nbr, col_nbr), dtype=bool)
        self._content = {}
        self._anim = None
        self._length_curves = 0

        if self.mode == PlotMode.LIVE_DYNAMIC:
            self._live_dynamic_data_queue = mp.Queue()
            socket_proc = mp.Process(
                target=launch_client,
                args=(
                    self._live_dynamic_data_queue,
                    host,
                    port,
                ),
            )
            socket_proc.start()
            self._no_more_values = False

    def add_subplot(
        self,
        subplot_name: str,
        row_idx: Union[slice, int, range],
        col_idx: Union[slice, int, range],
        subplot_type: SubplotType,
        unit: str,
        show_unit: bool,
        curves: dict,
    ):
        """
        Adds a new subplot to the plot at a position specified by row_idx and col_idx
        that should not be already taken by another subplot.

        :param subplot_name: name of the subplot that will be used as title
        :param row_idx: row indices of the subplot, should be contiguous
        :param col_idx: column indices of the subplot, should be contiguous
        :param subplot_type: type of the subplot. Should be either SubplotType.SPATIAL or SubplotType.TEMPORAL
        :param unit: unit of the subplot. Should be a string
        :type unit: str
        :param show_unit: whether to show the unit of the subplot in the title or not.
        :param curves: A dictionary of curves. The keys are the names of the curves and the
            values are dictionaries with the following keys:
            - data: the data to be plotted. None if the data is not yet known
            - options: a dictionary of options for the plot
        """
        # check that there is no plot at the specified position
        col_idx = _convert_to_contiguous_slice(col_idx)
        row_idx = _convert_to_contiguous_slice(row_idx)

        if subplot_name in self._content:
            raise ValueError("A subplot with the same name already exists")

        idx = np.ix_(range(self._row_nbr)[row_idx], range(self._col_nbr)[col_idx])
        if np.any(self._plot_positions[idx]):
            raise ValueError("The subplot superposes with other subplots")

        self._plot_positions[idx] = True

        # create the subplot
        ax = self._fig.add_subplot(self._gridspec[row_idx, col_idx])
        ax.autoscale_view()
        if subplot_type == SubplotType.SPATIAL:
            plt.axis("equal")

        # examine each curve
        assert isinstance(curves, dict)
        for curve_name, curve_values in curves.items():
            assert isinstance(curve_values, dict)
            assert "curve_style" in curve_values and "curve_type" in curve_values
            assert isinstance(curve_values["curve_type"], CurveType)
            assert isinstance(curve_values["curve_style"], CurvePlotStyle)

            if "data" not in curve_values:
                curve_values["data"] = None
            else:
                assert (
                    isinstance(curve_values["data"], np.ndarray)
                    or curve_values["data"] is None
                )
            if "mpl_options" not in curve_values:
                curve_values["mpl_options"] = {}
            else:
                assert isinstance(curve_values["mpl_options"], dict)

            if curve_values["curve_style"] == CurvePlotStyle.PLOT:
                plot_fun = ax.plot
            elif curve_values["curve_style"] == CurvePlotStyle.STEP:
                plot_fun = ax.step
            elif curve_values["curve_style"] == CurvePlotStyle.SCATTER:
                raise ValueError("fuck you mpl sucks")
            elif curve_values["curve_style"] == CurvePlotStyle.SEMILOGX:
                plot_fun = ax.semilogx
            elif curve_values["curve_style"] == CurvePlotStyle.SEMILOGY:
                plot_fun = ax.semilogy
            elif curve_values["curve_style"] == CurvePlotStyle.LOGLOG:
                plot_fun = ax.loglog
            else:
                raise ValueError("Unknown plot style: ", curve_values["curve_style"])
            curves[curve_name]["plot_fun"] = plot_fun

            # check the specified data for the curve
            # check that it has the right type
            # check the shape and size
            if subplot_type == SubplotType.TEMPORAL:
                if curve_values["curve_type"] == CurveType.STATIC:
                    assert curve_values["data"].ndim == 1
                elif curve_values["curve_type"] == CurveType.REGULAR:
                    if self.mode != PlotMode.LIVE_DYNAMIC:
                        assert curve_values["data"].ndim == 1
                        if self._length_curves == 0:
                            self._length_curves = curve_values["data"].shape[-1]
                        else:
                            assert self._length_curves == curve_values["data"].shape[-1]
                elif curve_values["curve_type"] == CurveType.PREDICTION:
                    if self.mode != PlotMode.LIVE_DYNAMIC:
                        assert curve_values["data"].ndim == 2
                        if self._length_curves == 0:
                            self._length_curves = curve_values["data"].shape[-1]
                        else:
                            assert self._length_curves == curve_values["data"].shape[-1]
                else:
                    raise ValueError("Unknown curve type: ", curve_values["curve_type"])
            elif subplot_type == SubplotType.SPATIAL:
                if curve_values["curve_type"] == CurveType.STATIC:
                    assert (
                        curve_values["data"].ndim == 2
                        and curve_values["data"].shape[0] == 2
                    )
                elif curve_values["curve_type"] == CurveType.REGULAR:
                    if self.mode != PlotMode.LIVE_DYNAMIC:
                        assert curve_values["data"].ndim == 2
                        if self._length_curves == 0:
                            self._length_curves = curve_values["data"].shape[-1]
                        else:
                            assert self._length_curves == curve_values["data"].shape[-1]

                elif curve_values["curve_type"] == CurveType.PREDICTION:
                    if self.mode != PlotMode.LIVE_DYNAMIC:
                        assert (
                            curve_values["data"].ndim == 3
                            and curve_values["data"].shape[0] == 2
                        )
                        if self._length_curves == 0:
                            self._length_curves = curve_values["data"].shape[-1]
                        else:
                            assert self._length_curves == curve_values["data"].shape[-1]
                else:
                    raise ValueError("Unknown curve type: ", curve_values["curve_type"])
            else:
                raise ValueError("Unknown subplot type: ", subplot_type)

        # update the _content dict with everything that was specified
        self._content[subplot_name] = {
            "row_idx": row_idx,
            "col_idx": col_idx,
            "unit": unit,
            "show_unit": show_unit,
            "subplot_type": subplot_type,
            "ax": ax,
            "curves": curves,
        }

    def plot(self, show: bool = True, save: bool = False, save_path: str = None):
        # for static, plot everything
        # for dynamic, plot static curves and use _update_dynamic for the animation
        # for live dynamic, plot static curves and use _update_live_dynamic for the animation
        # the curves that are not plotted (right now) are actually plotted as empty lines
        for subplot_name, subplot in self._content.items():
            # set subplot title
            subplot["ax"].set_title(
                subplot_name + " " + subplot["unit"]
                if subplot["show_unit"]
                else subplot_name
            )
            # plot all the curves inside
            for curve_name, curve in subplot["curves"].items():
                if (
                    curve["curve_type"] == CurveType.STATIC
                    or self.mode == PlotMode.STATIC
                ):
                    if subplot["subplot_type"] == SubplotType.TEMPORAL:
                        xdata = np.arange(curve["data"].size)
                        if self._sampling_time is not None:
                            xdata *= self._sampling_time
                        (line,) = curve["plot_fun"](
                            xdata, curve["data"], **curve["mpl_options"]
                        )
                    elif subplot["subplot_type"] == SubplotType.SPATIAL:
                        (line,) = curve["plot_fun"](
                            curve["data"][0, :],
                            curve["data"][1, :],
                            **curve["mpl_options"]
                        )
                    else:
                        raise ValueError(
                            "Unknown subplot type: ", subplot["subplot_type"]
                        )
                else:
                    (line,) = curve["plot_fun"]([], [], **curve["mpl_options"])

                curve["line"] = line

        # create animation if necessary
        if self.mode == PlotMode.DYNAMIC:
            self._anim = FuncAnimation(
                self._fig,
                self._update_dynamic,
                frames=self._length_curves,
                interval=self._interval,
                blit=True,
            )
        elif self.mode == PlotMode.LIVE_DYNAMIC:
            self._anim = FuncAnimation(
                self._fig,
                self._update_live_dynamic,
                frames=self._live_dynamic_generator,
                interval=self._interval,
                blit=True,
            )

        if save:
            if self.mode == PlotMode.DYNAMIC:
                assert save_path is not None, "save_path should be specified"
                self._anim.save(
                    save_path, fps=30, extra_args=["-vcodec", "libx264"], dpi=300
                )
            else:
                warnings.warn("cannot save static and live dynamic plots")

        elif show:
            # plt.show(block=False)
            plt.show(block=True)

    def _live_dynamic_generator(self):
        n = 0
        while not self._no_more_values:
            yield n
            n += 1

    def _update_dynamic(self, frame: int):
        if self.mode != PlotMode.DYNAMIC:
            raise ValueError("_update_dynamic should only be called in dynamic mode")
        else:
            return self._update_common(frame, live_dynamic=False)

    def _update_live_dynamic(self, frame):
        if self.mode != PlotMode.LIVE_DYNAMIC:
            raise ValueError(
                "_update_live_dynamic should only be called in live dynamic mode"
            )
        else:
            # first fetch new data via socket
            di = self._live_dynamic_data_queue.get(block=True)
            if di == STOP_SIGNAL:
                self._no_more_values = True
            else:
                assert type(di) is dict
                for subplot_name, subplot in di.items():
                    for curve_name, curve in subplot.items():

                        just_assign_dont_worry = (
                            self._content[subplot_name]["curves"][curve_name]["data"]
                            is None
                        )

                        if (
                            self._content[subplot_name]["subplot_type"]
                            == SubplotType.SPATIAL
                        ):
                            if (
                                self._content[subplot_name]["curves"][curve_name][
                                    "curve_type"
                                ]
                                == CurveType.REGULAR
                            ):
                                assert type(curve) is np.ndarray
                                assert curve.shape == (2,)
                                if just_assign_dont_worry:
                                    self._content[subplot_name]["curves"][curve_name][
                                        "data"
                                    ] = np.expand_dims(curve, 1)
                                else:
                                    self._content[subplot_name]["curves"][curve_name][
                                        "data"
                                    ] = np.append(
                                        self._content[subplot_name]["curves"][
                                            curve_name
                                        ]["data"],
                                        np.expand_dims(curve, 1),
                                        axis=1,
                                    )
                            elif (
                                self._content[subplot_name]["curves"][curve_name][
                                    "curve_type"
                                ]
                                == CurveType.PREDICTION
                            ):
                                assert type(curve) is np.ndarray
                                if not just_assign_dont_worry:
                                    assert (
                                        curve.shape
                                        == self._content[subplot_name]["curves"][
                                            curve_name
                                        ]["data"].shape
                                    )
                                self._content[subplot_name]["curves"][curve_name][
                                    "data"
                                ] = curve
                            else:
                                raise ValueError("big bruh")
                        elif (
                            self._content[subplot_name]["subplot_type"]
                            == SubplotType.TEMPORAL
                        ):
                            if (
                                self._content[subplot_name]["curves"][curve_name][
                                    "curve_type"
                                ]
                                == CurveType.REGULAR
                            ):
                                assert type(curve) is float
                                if just_assign_dont_worry:
                                    self._content[subplot_name]["curves"][curve_name][
                                        "data"
                                    ] = np.expand_dims(curve, 0)
                                else:
                                    self._content[subplot_name]["curves"][curve_name][
                                        "data"
                                    ] = np.append(
                                        self._content[subplot_name]["curves"][
                                            curve_name
                                        ]["data"],
                                        np.expand_dims(curve, 0),
                                        axis=0,
                                    )
                            elif (
                                self._content[subplot_name]["curves"][curve_name][
                                    "curve_type"
                                ]
                                == CurveType.PREDICTION
                            ):
                                assert type(curve) is np.ndarray
                                assert len(curve.shape) == 1
                                # if not just_assign_dont_worry:
                                #     assert (
                                #         curve.shape
                                #         == self._content[subplot_name]["curves"][
                                #             curve_name
                                #         ]["data"].shape
                                #     )
                                self._content[subplot_name]["curves"][curve_name][
                                    "data"
                                ] = curve
                            else:
                                raise ValueError("big bruh")
                        else:
                            raise ValueError("bruh")

            # update the plot
            return self._update_common(frame, live_dynamic=True)

    def _update_common(self, frame: int, live_dynamic: bool = False):
        artists = []
        for subplot_name, subplot in self._content.items():
            for curve_name, curve in subplot["curves"].items():
                if subplot["subplot_type"] == SubplotType.TEMPORAL:
                    if curve["curve_type"] != CurveType.STATIC:
                        if curve["curve_type"] == CurveType.REGULAR:
                            xdata = np.arange(frame + 1)
                        else:
                            # we have curve["curve_type"] == CurveType.PREDICTION
                            xdata = np.arange(curve["data"].size) + frame

                        if self._sampling_time is not None:
                            xdata *= self._sampling_time

                        # curve["line"].set_data(
                        #     xdata, curve["data"] if live_dynamic else curve["data"][:frame]
                        # )
                        # print(curve["curve_type"], xdata.shape, curve["data"][:frame+1].shape)
                        curve["line"].set_data(
                            xdata,
                            curve["data"][: frame + 1]
                            if curve["curve_type"] == CurveType.REGULAR
                            else curve["data"],
                        )

                        artists.append(curve["line"])

                elif subplot["subplot_type"] == SubplotType.SPATIAL:
                    if curve["curve_type"] != CurveType.STATIC:
                        if curve["curve_type"] == CurveType.REGULAR:
                            curve["line"].set_data(
                                curve["data"][0, : frame + 1],
                                curve["data"][1, : frame + 1],
                            )
                        elif curve["curve_type"] == CurveType.PREDICTION:
                            curve["line"].set_data(
                                curve["data"][0, :, frame]
                                if not live_dynamic
                                else curve["data"][0, :],
                                curve["data"][1, :, frame]
                                if not live_dynamic
                                else curve["data"][1, :],
                            )

                        artists.append(curve["line"])
                else:
                    raise ValueError("Unknown subplot type: ", subplot["subplot_type"])

        return artists


def _convert_to_contiguous_slice(idx: Union[slice, int, range]) -> slice:
    """Converts an index to a slice if it is not already a slice"""
    if type(idx) is slice:
        pass
    elif type(idx) is range:
        assert idx.step is None or idx.step == 1
        idx = slice(idx.start, idx.stop, 1)
    elif type(idx) is int:
        idx = slice(idx, idx + 1)
    else:
        raise ValueError("idx must be a slice, an int or a range")

    if idx.step is not None and idx.step != 1:
        raise ValueError("idx must be a contiguous slice")

    return idx


if __name__ == "__main__":
    pass
