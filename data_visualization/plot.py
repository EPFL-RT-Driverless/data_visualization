# from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional

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

    _fig: Figure
    _gridspec: GridSpec
    _row_nbr: int
    _col_nbr: int
    _plot_positions: np.ndarray  # np.array of bools
    _content: dict
    _mode: Mode
    _anim: Optional[FuncAnimation]

    def __init__(self, row_nbr: int, col_nbr: int, mode: Mode):
        self._fig = plt.figure()
        self._gridspec = self._fig.add_gridspec(row_nbr, col_nbr)
        self._row_nbr = row_nbr
        self._col_nbr = col_nbr
        self._plot_positions = np.zeros((row_nbr, col_nbr), dtype=bool)
        self._content = {}
        if mode != Plot.Mode.STATIC:
            raise NotImplementedError(
                "Dynamic and Live Dynamice modes are not implemented yet"
            )
        self._mode = mode
        self._anim = None

    def add_subplot(
        self,
        name: str,
        row_idx: slice,
        col_idx: slice,
        subplot_type: SubplotType,
        unit: str,
        show_unit: bool,
        curves: dict,
    ):
        """
        The positions inidcated by row_idx and col_idx should be unoccupied and should
        form a contiguous rectangle (i.e. the lists have to be both contiguous)..
        All the curves inside the subplot should have the same units for xdata and ydata.
        """
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

        # examine the specified data and plot everything
        if self._mode == Plot.Mode.STATIC:
            for curve_name, curve_values in curves.items():
                assert type(curve_values) is dict
                assert "data" in curve_values.keys()
                assert type(curve_values["data"]) is np.ndarray
                assert "options" in curve_values.keys()
                assert type(curve_values["options"]) is dict

                # if we don't specify any data, we plot an empty array
                if curve_values["data"].size == 0:
                    (line,) = ax.plot([], [], **curve_values["options"])
                else:
                    (line,) = ax.plot(
                        curve_values["data"][0, :],
                        curve_values["data"][1, :],
                        **curve_values["options"],
                    )

                # we add the matplotlib.lines.Line2D to the dict describing the curve
                curves[curve_name]["line"] = line

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
            # we should have already raised an error if the Display mode was not STATIC
            pass

    def get_subplot_names(self):
        """Returns the names of all the subplots and the curves inside them"""
        res = self._content
        for subplot_name, subplot in res.items():
            res[subplot_name] = subplot["curves"].keys()
        return res

    # def init_animation(self):
    #     pass
    #
    # # @abstractmethod
    # def animate(self, data: dict):
    #     if len(data) == 0:
    #         # we did not specify any data so we are going to use the one already specified at the creation of the subplots.
    #         # we either display the animation, or only the result
    #         try:
    #             pass
    #         except Exception:
    #             raise ValueError("You did not specify data")
    #
    #     for subplot_name, subplot_curves in data.items():
    #
    #
    # def create_animation(
    #     self, show: bool = True, save: bool = False, filename: str = None
    # ):
    #     self.anim = animation.FuncAnimation(
    #         self.fig,
    #         self.animate,
    #         # init_func=init_animation,
    #         frames=len(self.data["curves"]["X"]),
    #         # interval=1000 / sampling_time,
    #         blit=True,
    #     )
    #     if show:
    #         plt.show()
    #     if save:
    #         self.anim.save(filename, fps=30, extra_args=["-vcodec", "libx264"])

    # def animate_live(self):
    #     pass
    #
    # def _init_animation_from_existing_data(self):
    #     data_size = None
    #     # check that all the data has the same size
    #     content_names = self.get_subplot_names()
    #     for subplot_name, curve_names in content_names.items():
    #         for curve_name in curve_names:
    #             curve_description = self._content[subplot_name]["curves"][curve_name]
    #             size = curve_description["data"].shape[-1]
    #             if size is None:
    #                 size = data_size
    #             elif size != data_size:
    #                 raise ValueError(
    #                     "All the curve data don't have the same number of values."
    #                 )
    #
    #     # define the callback that updates the animation
    #     def update_anim(i):
    #         for subplot_name, curve_names in content_names.items():
    #             for curve_name in curve_names:
    #                 curve_description = self._content[subplot_name]["curves"][
    #                     curve_name
    #                 ]
    #                 curve_description["line"].set_data(
    #                     curve_description["data"][:, :, i]
    #                     if curve_description["prediction"]
    #                     else curve_description["data"][:, :i]
    #                 )
    #
    #     return FuncAnimation(self._fig, update_anim, data_size)
    #
    # def animate_from_existing_data(self):
    #     self._init_animation_from_existing_data()
    #     plt.show()
    #
    # def save_animation(self, filename: str, fps: int):
    #     anim = self._init_animation_from_existing_data()
    #     anim.save(filename, fps=fps)
