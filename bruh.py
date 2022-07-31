from abc import ABC, abstractmethod

import matplotlib.figure
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.gridspec import GridSpec


class Plot(ABC):
    fig: matplotlib.figure.Figure
    anim: FuncAnimation
    gridspec: GridSpec
    plot_positions: np.ndarray  # np.array of bools
    content: dict

    def __init__(self, row_nbr: int, col_nbr: int):
        self.fig = plt.figure()
        self.gridspec = self.fig.add_gridspec(row_nbr, col_nbr)
        self.plot_positions = np.zeros((row_nbr, col_nbr), dtype=bool)
        self.anim = None

    def add_subplot(
        self,
        name: str,
        row_idx: list,
        col_idx: list,
        unit: str,
        show_unit: bool,
        curves: dict,
        **kwargs,
    ):
        """
        The positions inidcated by row_idx and col_idx should be unoccupied and should form a contiguous rectangle (i.e. the lists have to be both contiguous)..
        All the curves inside the subplot should have the same units for xdata and ydata.
        """
        # check that row_idx and col_idx are contiguous, or basically that they correspond to a range
        sorted_col_idx = sorted(col_idx)
        sorted_row_idx = sorted(row_idx)
        if row_idx != range(
            sorted_row_idx[0], sorted_row_idx[0] + len(sorted_row_idx)
        ) or col_idx != range(
            sorted_col_idx[0], sorted_col_idx[0] + len(sorted_col_idx)
        ):
            raise ValueError("row_idx and col_idx must be contiguous")

        # check if the plot does not conflict with a pre-existing one
        if name in self.content:
            raise ValueError("A subplot with the same name already exists")

        if np.any(self.plot_positions[np.ix_[row_idx, col_idx]]):
            raise ValueError("The subplot superposes with other subplots")

        self.plot_positions[np.ix_[row_idx, col_idx]] = True
        # self.data[name] = {
        #     "row_idx": row_idx,
        #     "col_idx": col_idx,
        #     "unit": kwargs.get("unit", ""),
        #     "show_unit": kwargs.get("show_unit", True),
        #     "temporal": kwargs.get("temporal", True),
        #     "curves": kwargs.get("curves", {}),
        #     # each key corresponds to the name of a curve, and the value corresponds to a Tuple with a curve (something plotted in matplotlib) and a np.ndarray of shape (2,n) corresponding to the values to be plotted
        #     # "curves" = {
        #     #       "curve_1": (curve, np.array([[x1, x2, ...], [y1, y2, ...]])),
        #     #       ...
        #     # }
        #     # all the values should have the same lengths
        #     # Ok so basically, if the plot is not live, we can just give all the data
        #     # from the beginning (for the predictions, we should give a (n,p) array
        #     # corresponding to the values taken over time), check that they have the
        #     # same length, and then plot them by iterating.
        #     # if the plot is live, bro idk. We should subclass Plot and redefine the
        #     # method that is uses as callback to update the plot in FuncAnimation.
        #     # This method would somehow fetch data that would be updated outside ?
        #     # We give it references to the part of the data that should be plotted (states_data[0,k], pred_x[0,:] and the corresponding x values)
        #     # The problem is that these values should be updated before the plot is updated, and we need a way to enforce this happens and that we don't plot data that is not yet updated
        #     # We could create a bool called updated, that is set to False every time the plot is updated and to True every time the data is updates.
        # }

        ax = self.fig.add_subplot(self.gridspec[row_idx, col_idx])
        for curve_name, curve_values in curves.items():
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

        self.content[name] = {
            "row_idx": row_idx,
            "col_idx": col_idx,
            "unit": unit,
            "show_unit": show_unit,
            "temporal": True,
            "ax": ax,
            "curves": curves,
        }

    def get_subplot_names(self):
        """Returns the names of all the subplots and the curves inside them"""
        res = self.content
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

    def animate_live(self):
        pass

    def _init_animation_from_existing_data(self):
        data_size = None
        # check that all the data has the same size
        content_names = self.get_subplot_names()
        for subplot_name, curve_names in content_names.items():
            for curve_name in curve_names:
                curve_description = self.content[subplot_name]["curves"][curve_name]
                size = curve_description["data"].shape[-1]
                if size is None:
                    size = data_size
                elif size != data_size:
                    raise ValueError(
                        "All the curve data don't have the same number of values."
                    )

        # define the callback that updates the animation
        def update_anim(i):
            for subplot_name, curve_names in content_names.items():
                for curve_name in curve_names:
                    curve_description = self.content[subplot_name]["curves"][curve_name]
                    curve_description["line"].set_data(
                        curve_description["data"][:, :, i]
                        if curve_description["prediction"]
                        else curve_description["data"][:, :i]
                    )

        return FuncAnimation(self.fig, update_anim, data_size)

    def animate_from_existing_data(self):
        self._init_animation_from_existing_data()
        plt.show()

    def save_animation(self, filename: str, fps: int):
        anim = self._init_animation_from_existing_data()
        anim.save(filename, fps=fps)



if __name__ ==  "__main__":
    plot = Plot(4,2)
    plot.add_subplot(
        {
        #     "row_idx": row_idx,
        #     "col_idx": col_idx,
        #     "unit": kwargs.get("unit", ""),
        #     "show_unit": kwargs.get("show_unit", True),
        #     "temporal": kwargs.get("temporal", True),
        #     "curves": kwargs.get("curves", {}),
        #     # each key corresponds to the name of a curve, and the value corresponds to a Tuple with a curve (something plotted in matplotlib) and a np.ndarray of shape (2,n) corresponding to the values to be plotted
        #     # "curves" = {
        #     #       "curve_1": (curve, np.array([[x1, x2, ...], [y1, y2, ...]])),
        #     #       ...
        #     # }
        #     # all the values should have the same lengths
        #     # Ok so basically, if the plot is not live, we can just give all the data
        #     # from the beginning (for the predictions, we should give a (n,p) array
        #     # corresponding to the values taken over time), check that they have the
        #     # same length, and then plot them by iterating.
        #     # if the plot is live, bro idk. We should subclass Plot and redefine the
        #     # method that is uses as callback to update the plot in FuncAnimation.
        #     # This method would somehow fetch data that would be updated outside ?
        #     # We give it references to the part of the data that should be plotted (states_data[0,k], pred_x[0,:] and the corresponding x values)
        #     # The problem is that these values should be updated before the plot is updated, and we need a way to enforce this happens and that we don't plot data that is not yet updated
        #     # We could create a bool called updated, that is set to False every time the plot is updated and to True every time the data is updates.
        }
    )