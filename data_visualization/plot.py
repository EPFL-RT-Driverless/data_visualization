#  Copyright (c) 2022. Tudor Oancea EPFL Racing Team Driverless
import warnings
from enum import Enum
from typing import Optional, Union, Callable

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.figure import Figure
from matplotlib.gridspec import GridSpec

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

    def __init__(
        self,
        mode: PlotMode,
        row_nbr: int,
        col_nbr: int,
        interval: Optional[int] = None,
        sampling_time: Optional[float] = None,
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
                assert isinstance(curve_values["data"], np.ndarray)
            if "mpl_options" not in curve_values:
                curve_values["mpl_options"] = {}
            else:
                assert isinstance(curve_values["mpl_options"], dict)

            if curve_values["curve_style"] == CurvePlotStyle.PLOT:
                plot_fun = ax.plot
            elif curve_values["curve_style"] == CurvePlotStyle.STEP:
                plot_fun = ax.step
            elif curve_values["curve_style"] == CurvePlotStyle.SCATTER:
                plot_fun = ax.scatter
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

    def plot(self, show: bool = True, save: bool = True, save_path: str = None):
        # for static, plot everything
        # for dynamic, plot static curves and use _update_dynamic for the animation
        # for live dynamic, plot static curves and use _update_live_dynamic for the animation
        # the curves that are not plotted (right now) are actually plotted as empty lines
        for subplot_name, subplot in self._content.items():
            # set subplot title
            subplot["ax"].title(
                subplot_name + " " + subplot["unit"]
                if subplot["show_unit"]
                else subplot_name
            )
            # plot all the curves inside
            for curve_name, curve in self._content["curves"].items():
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
            anim = FuncAnimation(
                self._fig,
                self._update_dynamic,
                frames=self._length_curves,
                interval=self._interval,
                blit=True,
            )
        elif self.mode == PlotMode.LIVE_DYNAMIC:
            anim = FuncAnimation(
                self._fig,
                self._update_live_dynamic,
                interval=self._interval,
                blit=True,
            )
        else:
            anim = None

        if save:
            assert save_path is not None, "save_path should be specified"
            try:
                anim.save(save_path, fps=30, extra_args=["-vcodec", "libx264"], dpi=300)
            except:
                warnings.warn("cannot save static plots")
        elif show:
            plt.show(block=False)

    def _update_dynamic(self, iteration: int):
        if self.mode != PlotMode.DYNAMIC:
            raise ValueError("_update_dynamic should only be called in dynamic mode")
        else:
            artists = []
            for subplot_name, subplot in self._content.items():
                for curve_name, curve in subplot["curves"].items():
                    if subplot["subplot_type"] == SubplotType.TEMPORAL:
                        xdata = np.arange(iteration)
                        if curve["curve_type"] == CurveType.REGULAR:
                            if self._sampling_time is not None:
                                xdata *= self._sampling_time

                            curve["line"].set_data(xdata, curve["data"][:iteration])
                            artists.append(curve["line"])
                        elif curve["curve_type"] == CurveType.PREDICTION:
                            xdata += curve["data"].shape[0]
                            if self._sampling_time is not None:
                                xdata *= self._sampling_time

                            curve["line"].set_data(xdata, curve["data"][:, iteration])
                            artists.append(curve["line"])

                    elif subplot["subplot_type"] == SubplotType.SPATIAL:
                        if curve["curve_type"] == CurveType.REGULAR:
                            curve["line"].set_data(
                                curve["data"][0, :iteration],
                                curve["data"][1, :iteration],
                            )
                            artists.append(curve["line"])
                        elif curve["curve_type"] == CurveType.PREDICTION:
                            curve["line"].set_data(
                                curve["data"][0, :, iteration],
                                curve["data"][1, :, iteration],
                            )
                            artists.append(curve["line"])
                    else:
                        raise ValueError(
                            "Unknown subplot type: ", subplot["subplot_type"]
                        )

            return artists

    def _update_live_dynamic(self):
        # TODO: implement this
        if self.mode != PlotMode.LIVE_DYNAMIC:
            raise ValueError(
                "_update_live_dynamic should only be called in live dynamic mode"
            )
        else:
            pass


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
