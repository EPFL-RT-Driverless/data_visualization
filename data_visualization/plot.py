import warnings
from enum import Enum
from typing import Optional, Union, Callable

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.figure import Figure
from matplotlib.gridspec import GridSpec


class Plot:
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

    _fig: Figure
    _gridspec: GridSpec
    _row_nbr: int
    _col_nbr: int
    _interval: int
    _sampling_time: Optional[float]
    _plot_positions: np.ndarray  # np.array of bools
    _content: dict
    _anim: Optional[FuncAnimation]

    def __init__(
        self,
        row_nbr: int,
        col_nbr: int,
        interval: int = 100,
        sampling_time: Optional[float] = None,
    ):
        """
        Initializes the plot with an empty Gridspec of size row_nbr x col_nbr.

        :param row_nbr: number of rows
        :param col_nbr: number of columns
        """
        # if mode != Plot.Mode.STATIC:
        #     raise NotImplementedError(
        #         "Dynamic and Live Dynamic modes are not implemented yet"
        #     )

        self._fig = plt.figure()
        self._gridspec = self._fig.add_gridspec(row_nbr, col_nbr)
        self._row_nbr = row_nbr
        self._col_nbr = col_nbr
        self._interval = interval
        self._sampling_time = sampling_time
        self._plot_positions = np.zeros((row_nbr, col_nbr), dtype=bool)
        self._content = {}

        # self._mode = mode
        self._anim = None

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
        :param row_idx: row indices of the subplot. Should be a contiguous slice object (i.e. step == 1 or step == None)
        :param col_idx: column indices of the subplot. Should be a contiguous slice object (i.e. step == 1 or step == None)
        :param subplot_type: type of the subplot. Should be either Plot.SubplotType.SPATIAL or Plot.SubplotType.TEMPORAL
        :param unit: unit of the subplot. Should be a string
        :type unit: str
        :param show_unit: whether to show the unit of the subplot in the title or not.
        :param curves: A dictionary of curves. The keys are the names of the curves and the
        values are dictionaries with the following keys:
        - data: the data to be plotted. None if the data is not yet known
        - options: a dictionary of options for the plot
        """
        col_idx = convert_to_contiguous_slice(col_idx)
        row_idx = convert_to_contiguous_slice(row_idx)

        if subplot_name in self._content:
            raise ValueError("A subplot with the same name already exists")

        idx = np.ix_(range(self._row_nbr)[row_idx], range(self._col_nbr)[col_idx])
        if np.any(self._plot_positions[idx]):
            raise ValueError("The subplot superposes with other subplots")

        self._plot_positions[idx] = True

        # create the subplot
        ax = self._fig.add_subplot(self._gridspec[row_idx, col_idx])
        if subplot_type == Plot.SubplotType.SPATIAL:
            plt.axis("equal")

        # examine the specified data
        length_curves = (
            0  # to see if all the regular curves in the plot  have the same length
        )
        for curve_name, curve_values in curves.items():
            assert type(curve_values) is dict
            assert "data" in curve_values.keys()
            assert (
                type(curve_values["data"]) is type(None)
                or type(curve_values["data"]) is np.ndarray
            )
            assert "options" in curve_values.keys()
            assert type(curve_values["options"]) is dict

            # extract the type of the curve (static, regular, prediction)
            curve_type: Plot.CurveType = curve_values["options"].pop("is_prediction")
            curves[curve_name]["curve_type"] = curve_type

            # extract the desired plot style
            plot_style: Plot.CurvePlotStyle = curve_values["options"].pop(
                "curve_style", Plot.CurvePlotStyle.PLOT
            )
            if plot_style == Plot.CurvePlotStyle.PLOT:
                plot_fun = ax.plot
            elif plot_style == Plot.CurvePlotStyle.STEP:
                plot_fun = ax.step
            elif plot_style == Plot.CurvePlotStyle.SCATTER:
                plot_fun = ax.scatter
            elif plot_style == Plot.CurvePlotStyle.SEMILOGX:
                plot_fun = ax.semilogx
            elif plot_style == Plot.CurvePlotStyle.SEMILOGY:
                plot_fun = ax.semilogy
            elif plot_style == Plot.CurvePlotStyle.LOGLOG:
                plot_fun = ax.loglog
            else:
                raise ValueError("Unknown plot style: ", plot_style)
            curves[curve_name]["plot_fun"] = plot_fun

            # check the specified data to be plotted
            # if STATIC, plot everything. Nothing should be None, everything should be specified
            # if DYNAMIC or LIVE_DYNAMIC, only plot the static curves and plot the rest
            # in the update function in FuncAnimation. We don't specify init_func

            if (
                self.__class__ == StaticPlot
                or self.__class__ == DynamicPlot
                or (
                    self.__class__ == LiveDynamicPlot
                    and curve_type == Plot.CurveType.STATIC
                )
            ):
                assert (
                    curve_type != Plot.CurveType.PREDICTION
                ), "Static plots cannot contain predictions"
                assert (
                    curve_values["data"] is not None
                ), "All the data should be specified for static plots but its not the case for curve {}".format(
                    curve_name
                )

                # check dimensions of data
                if subplot_type == Plot.SubplotType.SPATIAL:
                    assert (
                        curve_values["data"].ndim == 2
                        and curve_values["data"].shape[0] == 2
                    ), "Spatial curves should have 2 rows"
                else:
                    if curve_type == Plot.CurveType.PREDICTION:
                        assert (
                            curve_values["data"].ndim == 2
                        ), "prediction curves should have 2 dims"
                    else:
                        assert curve_values["data"].ndim == 1

                # check that all the regular and prediction curves (not static nor predictions) have the same length
                # only happens for Static and Dynamic plots
                if (
                    curve_type == Plot.CurveType.REGULAR
                    or curve_type == Plot.CurveType.PREDICTION
                ):
                    if length_curves == 0:
                        length_curves = curve_values["data"].shape[-1]
                    else:
                        if curve_values["data"].shape[-1] != length_curves:
                            raise ValueError(
                                "The length of the regular curves in the plot should be the same"
                            )

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

    def get_subplot_names(self):
        """Returns the names of all the subplots and the curves inside them"""
        res = self._content
        for subplot_name, subplot in res.items():
            res[subplot_name] = subplot["curves"].keys()
        return res

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
                    curve["curve_type"] == Plot.CurveType.STATIC
                    or self.__class__ == StaticPlot
                ):
                    (line,) = self._plot_curve(
                        subplot_type=subplot["subplot_type"],
                        data=curve["data"],
                        options=curve["options"],
                        plot_fun=curve["plot_fun"],
                        curve_type=curve["curve_type"],
                    )
                else:
                    (line,) = curve["plot_fun"]([], [], **curve["options"])

                curve["line"] = line

        # create animation if necessary
        if self.__class__ == DynamicPlot:
            # TODO: pass the total length of the curves
            anim = FuncAnimation(
                self._fig, self._update_dynamic, interval=self._interval, blit=True
            )
        elif self.__class__ == LiveDynamicPlot:
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

    def _update_dynamic(self):
        # TODO: implement this
        pass

    def _update_live_dynamic(self):
        # TODO: implement this
        pass

    def _plot_curve(
        self,
        subplot_type: SubplotType,
        data: np.ndarray,
        options: dict,
        plot_fun: Callable,
        curve_type: CurveType,
    ):
        if subplot_type == self.SubplotType.SPATIAL:
            (line,) = plot_fun(
                data[0, :],
                data[1, :],
                **options,
            )
        else:
            xdata = np.arange(data.size)
            if curve_type == self.CurveType.PREDICTION:
                xdata += data.size

            if self._sampling_time is not None:
                xdata *= self._sampling_time

            (line,) = plot_fun(
                xdata,
                data,
                **options,
            )

        return (line,)


class StaticPlot(Plot):
    pass


class DynamicPlot(Plot):
    # uses ArtistAnimation
    pass


class LiveDynamicPlot(Plot):
    # uses FuncAnimation with small interval (1ms) which fetches
    pass


def convert_to_contiguous_slice(idx: Union[slice, int, range]) -> slice:
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
