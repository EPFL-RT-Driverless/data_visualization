from enum import Enum
from typing import Optional, Union

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.figure import Figure
from matplotlib.gridspec import GridSpec


class Plot:
    class Mode(Enum):
        STATIC = 0
        DYNAMIC = 1
        LIVE_DYNAMIC = 2

    class SubplotType(Enum):
        SPATIAL = 0
        TEMPORAL = 1

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
    _plot_positions: np.ndarray  # np.array of bools
    _content: dict
    _mode: Mode
    _anim: Optional[FuncAnimation]

    def __init__(self, row_nbr: int, col_nbr: int, mode: Mode):
        """
        Initializes the plot with an empty Gridspec of size row_nbr x col_nbr.

        :param row_nbr: number of rows
        :param col_nbr: number of columns
        :param mode: whether the plot should be static, dynamic, or live dynamic
        """
        if mode != Plot.Mode.STATIC:
            raise NotImplementedError(
                "Dynamic and Live Dynamice modes are not implemented yet"
            )

        self._fig = plt.figure()
        self._gridspec = self._fig.add_gridspec(row_nbr, col_nbr)
        self._row_nbr = row_nbr
        self._col_nbr = col_nbr
        self._plot_positions = np.zeros((row_nbr, col_nbr), dtype=bool)
        self._content = {}

        self._mode = mode
        self._anim = None

    def add_subplot(
        self,
        name: str,
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
        :param name: name of the subplot that will be used as title
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
        if type(row_idx) is range:
            assert row_idx.step is None or row_idx.step == 1
            row_idx = slice(row_idx.start, row_idx.stop, 1)
        if type(row_idx) is int:
            row_idx = slice(row_idx, row_idx + 1)
        if type(col_idx) is range:
            assert col_idx.step is None or col_idx.step == 1
            col_idx = slice(col_idx.start, col_idx.stop, 1)
        if type(col_idx) is int:
            col_idx = slice(col_idx, col_idx + 1)

        # give some default values
        if row_idx is None:
            row_idx = slice(0, self._row_nbr)
        if col_idx is None:
            col_idx = slice(0, self._col_nbr)

        # check that row_idx and col_idx are contiguous, or basically that they
        # correspond to a range
        if (row_idx.step is not None and row_idx.step != 1) or (
            col_idx.step is not None and col_idx.step != 1
        ):
            raise ValueError("row_idx and col_idx must be contiguous")

        # check if the plot the user wants to add does not conflict with a pre-existing
        # one
        if name in self._content:
            raise ValueError("A subplot with the same name already exists")

        idx = np.ix_(range(self._row_nbr)[row_idx], range(self._col_nbr)[col_idx])
        if np.any(self._plot_positions[idx]):
            raise ValueError("The subplot superposes with other subplots")

        self._plot_positions[idx] = True

        # create the subplot
        ax = self._fig.add_subplot(self._gridspec[row_idx, col_idx])
        if subplot_type == Plot.SubplotType.SPATIAL:
            plt.axis("equal")

        # examine the specified data and plot everything
        if self._mode == Plot.Mode.STATIC:
            for curve_name, curve_values in curves.items():
                assert type(curve_values) is dict
                assert "data" in curve_values.keys()
                assert type(curve_values["data"]) is np.ndarray
                assert "options" in curve_values.keys()
                assert type(curve_values["options"]) is dict

                # set subplot title
                ax.title(curve_name + " " + unit if show_unit else curve_name)

                # plot the data with the specified style
                # if we don't specify any data, we plot an empty array
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

                if curve_values["data"] is None or curve_values["data"].size == 0:
                    (line,) = plot_fun([], [], **curve_values["options"])
                else:
                    if (
                        len(curve_values["data"].shape) == 2
                        and curve_values["data"].shape[0] == 2
                    ):
                        (line,) = plot_fun(
                            curve_values["data"][0, :],
                            curve_values["data"][1, :],
                            **curve_values["options"],
                        )
                    else:
                        (line,) = plot_fun(
                            curve_values["data"], **curve_values["options"]
                        )

                # we add the matplotlib.lines.Line2D to the dict describing the curve
                curves[curve_name]["line"] = line

            # update the _content dict with everything that was specified
            self._content[name] = {
                "row_idx": row_idx,
                "col_idx": col_idx,
                "unit": unit,
                "show_unit": show_unit,
                "subplot_type": subplot_type,
                "ax": ax,
                "curves": curves,
            }
        else:
            # we should have already raised an error in __init__ if the Display mode was
            # not STATIC
            pass

    def get_subplot_names(self):
        """Returns the names of all the subplots and the curves inside them"""
        res = self._content
        for subplot_name, subplot in res.items():
            res[subplot_name] = subplot["curves"].keys()
        return res
