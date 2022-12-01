#  Copyright (c) 2022. Tudor Oancea, Mattéo Berthet, EPFL Racing Team Driverless
import multiprocessing as mp
import warnings
from enum import Enum
from time import perf_counter
from typing import Optional, Union

import cv2
import numpy as np
from matplotlib import pyplot as plt, style as mplstyle
from matplotlib.animation import FuncAnimation, FFMpegWriter, PillowWriter
from matplotlib.figure import Figure
from matplotlib.gridspec import GridSpec
import matplotlib as mpl

from matplotlib import style as mplstyle
from matplotlib import patches as ptc

from .constants import *
from .subscriber import launch_client

from .constants import *
from .subscriber import launch_client
from track_database import skidpad, acceleration_track

__all__ = ["Plot", "PlotMode", "SubplotType", "CurveType", "CurvePlotStyle"]


class MyFuncAnimation(FuncAnimation):
    def _end_redraw(self, event):
        # Now that the redraw has happened, do the post draw flushing and
        # blit handling. Then re-enable all of the original events.
        self._post_draw(None, True)
        self.event_source.start()
        self._fig.canvas.mpl_disconnect(self._resize_id)
        self._resize_id = self._fig.canvas.mpl_connect("resize_event", self._on_resize)


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


class Car:
    _trajectory: tuple
    _orientation: tuple
    _steering: tuple
    _show_car: bool

    def __init__(self):
        self._trajectory = None
        self._orientation = None
        self._steering = None
        self._show_car = False


class Plot(ErrorMessageMixin):
    """
    Description:
    -----------
    This class can be used to plot the evolution of several measures throughout time. A
    matplotlib figure is created containing a gridspec on which you can add subplots
    taking one or several (contiguous) positions. In these subplots you can add several
    curves with a great number of options of customization.
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

    # stuff for Dynamic mode
    _dynamic_current_frame: Optional[int]

    # stuff for Dynamic and Live Dynamic modes
    _redrawn_artists: Optional[list]

    # stuff for Live dynamic mode
    _live_dynamic_data_queue: Optional[mp.Queue]
    _no_more_values: Optional[bool]

    # value to show the cars or not and to know what to show
    _show_car: bool
    _cars: list
    _show_cars: bool

    def __init__(
        self,
        mode: PlotMode,
        row_nbr: int,
        col_nbr: int,
        figsize: tuple = (15, 6),
        interval: Optional[int] = None,
        sampling_time: Optional[float] = None,
        host: str = DEFAULT_HOST,
        port: int = DEFAULT_PORT,
        show_car=False,
        **kwargs,
    ):
        """
        Initializes the plot with an empty Gridspec of size row_nbr x col_nbr.

        :param mode: the mode of the plot. Can be STATIC, DYNAMIC, or LIVE_DYNAMIC
        :param row_nbr: number of rows
        :param col_nbr: number of columns
        :param interval: interval between frames in milliseconds, only needed for DYNAMIC and LIVE_DYNAMIC
        :param sampling_time: sampling time used in the experiment, only needed if the temporal subplots need to have an x axis with time instead of number of iteration
        """
        super().__init__(**kwargs)
        self.mode = mode
        self._row_nbr = row_nbr
        self._col_nbr = col_nbr
        self._sampling_time = sampling_time

        self._fig = plt.figure(figsize=figsize)
        self._gridspec = self._fig.add_gridspec(row_nbr, col_nbr)
        self._plot_positions = np.zeros((row_nbr, col_nbr), dtype=bool)
        self._content = {}
        self._anim = None
        self._length_curves = 0
        self._show_cars = show_car
        self._car_traj = False
        self._car_phi = False
        self._wheel_delta = False
        self._cars = []

        mplstyle.use("fast")

        if self.mode == PlotMode.DYNAMIC or self.mode == PlotMode.LIVE_DYNAMIC:
            self._redrawn_artists = []
            assert (
                interval is not None
            ), "interval must be specified for dynamic and live dynamic modes"
            self._interval = interval
        else:
            self._redrawn_artists = None
            self._interval = None

        if self.mode == PlotMode.LIVE_DYNAMIC:
            self._live_dynamic_data_queue = mp.Queue()
            socket_proc = mp.Process(
                target=launch_client,
                args=(self._live_dynamic_data_queue, host, port),
                kwargs=kwargs,
            )
            socket_proc.start()
            self._no_more_values = False
        else:
            self._live_dynamic_data_queue = None
            self._no_more_values = None

    def add_subplot(
        self,
        subplot_name: str,
        row_idx: Union[slice, int, range],
        col_idx: Union[slice, int, range],
        subplot_type: SubplotType,
        unit: str,
        show_unit: bool,
        curves: dict,
        car_data_type: str = None,
        car_data_names: list = None,
        car_ids: list = None,
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
        :param curves: A dictionary of curves.
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
                if curve_values["curve_type"] != CurveType.STATIC:
                    raise NotImplementedError(
                        "dynamic scatter curves are not yet implemented"
                    )

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
                            self._length_curves = curve_values["data"].shape[0]
                        else:
                            assert (
                                self._length_curves == curve_values["data"].shape[0]
                            ), "All curves must have the same length but this one has length {} while others have {}".format(
                                curve_values["data"].shape[0], self._length_curves
                            )
                elif curve_values["curve_type"] == CurveType.PREDICTION:
                    if self.mode != PlotMode.LIVE_DYNAMIC:
                        assert curve_values["data"].ndim == 2
                        if self._length_curves == 0:
                            self._length_curves = curve_values["data"].shape[0]
                        else:
                            assert (
                                self._length_curves == curve_values["data"].shape[0]
                            ), "All curves must have the same length but this one has length {} while others have {}".format(
                                curve_values["data"].shape[0], self._length_curves
                            )
                else:
                    raise ValueError("Unknown curve type: ", curve_values["curve_type"])
            elif subplot_type == SubplotType.SPATIAL:
                if curve_values["curve_type"] == CurveType.STATIC:
                    assert (
                        curve_values["data"].ndim == 2
                        and curve_values["data"].shape[1] == 2
                    )
                elif curve_values["curve_type"] == CurveType.REGULAR:
                    if self.mode != PlotMode.LIVE_DYNAMIC:
                        assert curve_values["data"].ndim == 2
                        if self._length_curves == 0:
                            self._length_curves = curve_values["data"].shape[0]
                        else:
                            assert (
                                self._length_curves == curve_values["data"].shape[0]
                            ), "All curves must have the same length but this one has length {} while others have {}".format(
                                curve_values["data"].shape[0], self._length_curves
                            )

                elif curve_values["curve_type"] == CurveType.PREDICTION:
                    if self.mode != PlotMode.LIVE_DYNAMIC:
                        assert (
                            curve_values["data"].ndim == 3
                            and curve_values["data"].shape[2] == 2
                        )
                        if self._length_curves == 0:
                            self._length_curves = curve_values["data"].shape[0]
                        else:
                            assert (
                                self._length_curves == curve_values["data"].shape[0]
                            ), "All curves must have the same length but this one has length {} while others have {}".format(
                                curve_values["data"].shape[0], self._length_curves
                            )
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

        # update the _subplot_names lis

        if (
            car_data_names is not None
            and car_data_type is not None
            and car_ids is not None
        ):
            assert len(car_data_names) == len(
                car_ids
            ), "car_data_name and car_id must have the same length"
            for a in range(len(car_ids)):
                i = car_ids[a]
                car_data_name = car_data_names[a]
                assert i <= len(self._cars) + 1, "Car index out of range"
                if len(self._cars) >= i:
                    i = i - 1
                    car_attribute = self._cars[i].__dict__[car_data_type]
                    if car_attribute is None:
                        car_attribute = (subplot_name, car_data_name)
                        if car_data_type == "_trajectory":
                            self._cars[i].show_car = True
                else:
                    i = i - 1
                    self._cars.append(Car())
                    self._cars[i].__dict__[car_data_type] = (
                        subplot_name,
                        car_data_name,
                    )
                    if car_data_type == "_trajectory":
                        self._cars[i]._show_car = True

    def plot(self, show: bool = True, save_path: str = None):
        for subplot_name, subplot in self._content.items():
            # set subplot title
            subplot["ax"].set_ylabel(
                "{} [{}]".format(subplot_name, subplot["unit"])
                if subplot["show_unit"]
                else subplot_name,
                labelpad=10,
            )
            # plot all the curves inside
            for curve_name, curve in subplot["curves"].items():
                if (
                    curve["curve_type"] == CurveType.STATIC
                    or self.mode == PlotMode.STATIC
                ):
                    if subplot["subplot_type"] == SubplotType.TEMPORAL:
                        xdata = np.arange(curve["data"].size, dtype=np.float)
                        if self._sampling_time is not None:
                            xdata *= self._sampling_time

                        if curve["curve_style"] != CurvePlotStyle.SCATTER:
                            (line,) = curve["plot_fun"](
                                xdata, curve["data"], **curve["mpl_options"]
                            )
                        else:
                            line = curve["plot_fun"](
                                xdata, curve["data"], **curve["mpl_options"]
                            )
                    elif subplot["subplot_type"] == SubplotType.SPATIAL:
                        if curve["curve_style"] != CurvePlotStyle.SCATTER:
                            (line,) = curve["plot_fun"](
                                curve["data"][:, 0],
                                curve["data"][:, 1],
                                **curve["mpl_options"],
                            )
                        else:
                            line = curve["plot_fun"](
                                curve["data"][:, 0],
                                curve["data"][:, 1],
                                **curve["mpl_options"],
                            )

                    else:
                        raise ValueError(
                            "Unknown subplot type: ", subplot["subplot_type"]
                        )
                else:
                    if curve["curve_style"] != CurvePlotStyle.SCATTER:
                        (line,) = curve["plot_fun"]([], [], **curve["mpl_options"])
                    else:
                        line = curve["plot_fun"]([], [], **curve["mpl_options"])

                    if self.mode != PlotMode.STATIC:
                        self._redrawn_artists.append(line)

                curve["line"] = line

        plt.tight_layout()

        # create animation if necessary
        if self.mode == PlotMode.DYNAMIC:
            self._dynamic_current_frame = 1
            self._anim = MyFuncAnimation(
                self._fig,
                self._update_plot_dynamic,
                frames=self._dynamic_frame,
                save_count=self._length_curves,
                interval=self._interval,
                repeat=False,
                blit=True,
            )
        elif self.mode == PlotMode.LIVE_DYNAMIC:
            self._anim = MyFuncAnimation(
                self._fig,
                self._update_plot_live_dynamic,
                frames=self._live_dynamic_generator,
                interval=1,
                repeat=False,
                blit=True,
            )

        if save_path is not None:
            if self.mode == PlotMode.DYNAMIC:
                # mpl.rcParams['animation.ffmpeg_path'] = r'C:\Users\Philippe\Downloads\ffmpeg-2022-11-03-git-5ccd4d3060-essentials_build\ffmpeg-2022-11-03-git-5ccd4d3060-essentials_build\bin\ffmpeg.exe'
                try:
                    self._anim.save(
                        filename=save_path,
                        # writer=PillowWriter(fps=20),
                        writer=FFMpegWriter(fps=20),
                        dpi=300,
                    )
                except Exception as e:
                    print("Error while saving animation: ", e)
                    print(
                        "If the error comes from a missing file please refer to the package documentation to install FFMpeg"
                    )
            else:
                warnings.warn("cannot save static and live dynamic plots")

        elif show:
            # plt.show(block=False)
            plt.show(block=True)

    def _dynamic_frame(self):
        n = 0
        while self._dynamic_current_frame - 1 < self._length_curves:
            yield n
            n += 1

    def _live_dynamic_generator(self):
        n = 0
        while not self._no_more_values:
            yield n
            n += 1

    def _update_plot_dynamic(self, frame: int):
        if self.mode != PlotMode.DYNAMIC:
            raise ValueError("_update_dynamic should only be called in dynamic mode")
        else:
            # print(frame)
            start_time = perf_counter()
            self._update_plot_common(self._dynamic_current_frame)
            end_time = perf_counter() - start_time
            self._dynamic_current_frame += int(
                (end_time / self._sampling_time) // 1 + 1
            )
            return self._redrawn_artists

    def _update_plot_live_dynamic(self, frame: int):
        if self.mode != PlotMode.LIVE_DYNAMIC:
            raise ValueError(
                "_update_live_dynamic should only be called in live dynamic mode"
            )
        else:
            have_to_update = False
            last_received_image = None
            while not self._live_dynamic_data_queue.empty():
                # first fetch new data via socket
                received_data = self._live_dynamic_data_queue.get(block=True)
                if received_data is None:
                    # There have been an UnpicklingError so we don't have new data and do not update the plot
                    pass
                else:
                    # define the function that will actually update the content of the plot, will be called with the
                    # appropriate dict
                    def update_content(di: dict):
                        try:
                            # first extract the data from the dict and check the types and shapes of everything
                            new_data = {}
                            for subplot_name, subplot in di.items():
                                new_data[subplot_name] = {}
                                for curve_name, curve in subplot.items():
                                    new_data[subplot_name][curve_name] = None
                                    just_assign_dont_worry = (
                                        self._content[subplot_name]["curves"][
                                            curve_name
                                        ]["data"]
                                        is None
                                    )

                                    if (
                                        self._content[subplot_name]["subplot_type"]
                                        == SubplotType.SPATIAL
                                    ):
                                        if (
                                            self._content[subplot_name]["curves"][
                                                curve_name
                                            ]["curve_type"]
                                            == CurveType.REGULAR
                                        ):
                                            self._print_status_message(
                                                "received spatial data"
                                            )
                                            assert type(curve) is np.ndarray, (
                                                "The data for the curve "
                                                + curve_name
                                                + " in the subplot "
                                                + subplot_name
                                                + " should be a numpy array but is "
                                                + str(type(curve))
                                            )
                                            assert curve.shape == (2,), (
                                                "The data for the curve "
                                                + curve_name
                                                + " in the subplot "
                                                + subplot_name
                                                + " should be a numpy array of shape (2,) but is "
                                                + str(curve.shape)
                                            )
                                            if just_assign_dont_worry:
                                                new_data[subplot_name][
                                                    curve_name
                                                ] = np.expand_dims(curve, 0)
                                            else:
                                                new_data[subplot_name][
                                                    curve_name
                                                ] = np.append(
                                                    self._content[subplot_name][
                                                        "curves"
                                                    ][curve_name]["data"],
                                                    np.expand_dims(curve, 0),
                                                    axis=0,
                                                )
                                        elif (
                                            self._content[subplot_name]["curves"][
                                                curve_name
                                            ]["curve_type"]
                                            == CurveType.PREDICTION
                                        ):
                                            assert type(curve) is np.ndarray, (
                                                "The data for the curve "
                                                + curve_name
                                                + " in the subplot "
                                                + subplot_name
                                                + " should be a numpy array but is "
                                                + str(type(curve))
                                            )
                                            if not just_assign_dont_worry:
                                                assert (
                                                    curve.shape
                                                    == self._content[subplot_name][
                                                        "curves"
                                                    ][curve_name]["data"].shape
                                                ), (
                                                    "The data for the curve "
                                                    + curve_name
                                                    + " in the subplot "
                                                    + subplot_name
                                                    + " should be a numpy array of shape "
                                                    + str(
                                                        self._content[subplot_name][
                                                            "curves"
                                                        ][curve_name]["data"].shape
                                                    )
                                                    + " but is "
                                                    + str(curve.shape)
                                                )
                                            new_data[subplot_name][curve_name] = curve
                                        else:
                                            self._print_status_message(
                                                "You sent data for a curve that is not regular or prediction, ignoring"
                                            )
                                    elif (
                                        self._content[subplot_name]["subplot_type"]
                                        == SubplotType.TEMPORAL
                                    ):
                                        if (
                                            self._content[subplot_name]["curves"][
                                                curve_name
                                            ]["curve_type"]
                                            == CurveType.REGULAR
                                        ):
                                            assert (
                                                isinstance(curve, float)
                                                or isinstance(curve, np.float64)
                                                or isinstance(curve, np.float32)
                                            ), (
                                                "The data for the curve "
                                                + curve_name
                                                + " in the subplot "
                                                + subplot_name
                                                + " should be a float but is "
                                                + str(type(curve))
                                            )

                                            if just_assign_dont_worry:
                                                self._content[subplot_name]["curves"][
                                                    curve_name
                                                ]["data"] = np.expand_dims(curve, 0)
                                            else:
                                                new_data[subplot_name][
                                                    curve_name
                                                ] = np.append(
                                                    self._content[subplot_name][
                                                        "curves"
                                                    ][curve_name]["data"],
                                                    np.expand_dims(curve, 0),
                                                    axis=0,
                                                )
                                        elif (
                                            self._content[subplot_name]["curves"][
                                                curve_name
                                            ]["curve_type"]
                                            == CurveType.PREDICTION
                                        ):
                                            assert type(curve) is np.ndarray, (
                                                "The data for the curve "
                                                + curve_name
                                                + " in the subplot "
                                                + subplot_name
                                                + " should be a numpy array but is "
                                                + str(type(curve))
                                            )
                                            assert len(curve.shape) == 1, (
                                                "The data for the curve "
                                                + curve_name
                                                + " in the subplot "
                                                + subplot_name
                                                + " should be a numpy array of shape (n,) but is "
                                                + str(curve.shape)
                                            )

                                            new_data[subplot_name][curve_name] = curve
                                        else:
                                            self._print_status_message(
                                                "You sent data for a curve that is not regular or prediction, ignoring"
                                            )
                                    else:
                                        raise ValueError(
                                            "The subplot type is not valid for subplot "
                                            + subplot_name
                                        )

                            # if everything is in order update the content
                            for subplot_name, subplot in new_data.items():
                                for curve_name, curve in subplot.items():
                                    if curve is not None:
                                        self._content[subplot_name]["curves"][
                                            curve_name
                                        ]["data"] = curve

                            # update the length of the curves
                            self._length_curves += 1
                            return True
                        except AssertionError as e:
                            # we don't update the plot because some data were not in
                            # the right format (we drop the frame)
                            self._print_status_message(
                                "Received data are not in the right format, ignoring. Error message: "
                                + str(e)
                            )
                            return False

                    if received_data == STOP_SIGNAL:
                        self._print_status_message("Received stop signal")
                        self._no_more_values = True
                        break
                    elif isinstance(received_data, dict):
                        try:
                            if update_content(received_data):
                                have_to_update = True
                        except AssertionError:
                            pass

                    elif isinstance(received_data, tuple):
                        # update the content of the plot
                        try:
                            assert isinstance(received_data[0], dict)
                            if update_content(received_data[0]):
                                have_to_update = True
                        except AssertionError:
                            pass

                        # update the data for the image
                        try:
                            last_received_image = cv2.imdecode(received_data[1], 1)
                        except Exception:
                            self._print_status_message("Received invalid image")
                            pass
                    else:
                        # the data is not a string, a dict or a tuple, so we don't update the plot
                        pass

            if have_to_update:
                self._update_plot_common(self._length_curves)

            if last_received_image is not None:
                cv2.imshow("image", last_received_image)
                cv2.waitKey(1)

        return self._redrawn_artists

    def _update_plot_common(self, curves_size: int):
        """
        Redraws all the Regular and Prediction curves in all the subplots. Supposes that the data has already been
        updated beforehand.

        :param curves_size: the common size of all the regular curves
        """
        if self.mode == PlotMode.LIVE_DYNAMIC and self._length_curves == 0:
            return
        # start_plotting = perf_counter() #to show the plotting time (see end of function)
        # i = 1
        for subplot_name, subplot in self._content.items():
            for curve_name, curve in subplot["curves"].items():
                if subplot["subplot_type"] == SubplotType.TEMPORAL:
                    if curve["curve_type"] != CurveType.STATIC:
                        # curves_size = min(curve["data"].shape[0], curves_size_input)
                        if curve["curve_type"] == CurveType.REGULAR:
                            xdata = np.arange(curves_size, dtype=np.float)
                        else:
                            # we have curve["curve_type"] == CurveType.PREDICTION
                            xdata = (
                                np.arange(curve["data"].shape[1], dtype=np.float)
                                + curves_size * curve["data"].shape[1]
                                - 1
                            )
                        if self._sampling_time is not None:
                            xdata *= self._sampling_time

                        if curve["curve_style"] != CurvePlotStyle.SCATTER:
                            curve["line"].set_data(
                                xdata,
                                curve["data"][:curves_size]
                                if curve["curve_type"] == CurveType.REGULAR
                                else curve["data"]
                                if curve["curve_type"] == CurveType.STATIC
                                else curve["data"][curves_size - 1],
                            )
                        else:
                            curve["line"].set_offsets(
                                np.array(
                                    [
                                        xdata,
                                        curve["data"][:curves_size]
                                        if curve["curve_type"] == CurveType.REGULAR
                                        else curve["data"],
                                    ]
                                ).T
                            )

                elif subplot["subplot_type"] == SubplotType.SPATIAL:
                    # curves_size = min(curve["data"].shape[0], curves_size_input)
                    if curve["curve_type"] != CurveType.STATIC:
                        if curve["curve_type"] == CurveType.REGULAR:
                            if curve["curve_style"] != CurvePlotStyle.SCATTER:
                                self._print_status_message(
                                    "plot " + str(curve["data"][:curves_size, 0])
                                )
                                curve["line"].set_data(
                                    curve["data"][:curves_size, 0],
                                    curve["data"][:curves_size, 1],
                                )
                            else:
                                self._print_status_message("scatter")
                                curve["line"].set_offsets(
                                    curve["data"][:curves_size, :],
                                )
                        elif curve["curve_type"] == CurveType.PREDICTION:
                            if curve["curve_style"] != CurvePlotStyle.SCATTER:
                                curve["line"].set_data(
                                    curve["data"][curves_size - 1, :, 0]
                                    if self.mode == PlotMode.DYNAMIC
                                    else curve["data"][:, 0],
                                    curve["data"][curves_size - 1, :, 1]
                                    if self.mode == PlotMode.DYNAMIC
                                    else curve["data"][:, 1],
                                )
                            else:
                                curve["line"].set_offsets(
                                    np.transpose(
                                        curve["data"][:, :, curves_size - 1]
                                        if self.mode == PlotMode.DYNAMIC
                                        else curve["data"]
                                    ),
                                )

                else:
                    raise ValueError("Unknown subplot type: ", subplot["subplot_type"])

            subplot["ax"].relim()
            subplot["ax"].autoscale_view()

        if self._show_cars:
            for car in self._cars:
                if car._show_car:
                    translate = self._content[car._trajectory[0]]["curves"][
                        car._trajectory[1]
                    ]["data"][curves_size - 1]

                    phi = np.pi
                    if (
                        self._car_phi
                        and len(
                            self._content[car._orientation[0]]["curves"][
                                car._orientation[1]
                            ]["data"]
                        )
                        > curves_size
                    ):
                        phi = np.deg2rad(
                            self._content[car._orientation[0]]["curves"][
                                car._orientation[1]
                            ]["data"][curves_size - 1]
                            - 90
                        )

                    delta = 0
                    if (
                        self._wheel_delta
                        and len(
                            self._content[car._steering[0]]["curves"][car._steering[1]][
                                "data"
                            ]
                        )
                        > curves_size
                    ):
                        delta = np.deg2rad(
                            self._content[car._steering[0]]["curves"][car._steering[1]][
                                "data"
                            ][curves_size - 1]
                        )

                    # car measurements
                    h_car = 2.986
                    w_car = 0.951
                    th_car = 1.551
                    h_wheel = 0.3
                    w_wheel = 0.15
                    diff_car_wheel_h = 1.416
                    center_to_wheels = 1.403 / 2
                    h_body = 1.570 - h_wheel - 0.1
                    w_body = 1.403 + w_wheel
                    h_spoiler = 0.7
                    w_spoiler = 1.551

                    rotation_phi = np.array(
                        [[np.cos(phi), -np.sin(phi)], [np.sin(phi), np.cos(phi)]]
                    )
                    # car body
                    pos = np.array([-w_car / 2, -h_car / 2])
                    pos = rotation_phi @ pos + translate
                    car_body = ptc.Rectangle(
                        pos, w_car, h_car, angle=np.rad2deg(phi), color="red"
                    )

                    # front spoiler
                    pos = np.array([-w_spoiler / 2, h_car / 2 - h_spoiler])
                    pos = rotation_phi @ pos + translate
                    front_spoiler = ptc.Rectangle(
                        pos, w_spoiler, h_spoiler, angle=np.rad2deg(phi), color="C1"
                    )

                    # body between front and rear wheels
                    pos = np.array(
                        [
                            -center_to_wheels - w_wheel / 2,
                            h_car / 2 - h_spoiler - h_body - h_wheel - 0.2,
                        ]
                    )
                    pos = rotation_phi @ pos + translate
                    rear_spoiler = ptc.Rectangle(
                        pos, w_body, h_body, angle=np.rad2deg(phi), color="red"
                    )

                    # phi + delta rotation matrix
                    rotation_theta_phi = np.array(
                        [
                            [np.cos(delta + phi), -np.sin(delta + phi)],
                            [np.sin(delta + phi), np.cos(delta + phi)],
                        ]
                    )
                    # wheel top left
                    pos_wtl = np.array([-w_wheel / 2, -h_wheel / 2])
                    translate_wtl = (
                        rotation_phi
                        @ np.array(
                            [
                                -center_to_wheels + 0.05,
                                h_car / 2 - h_spoiler - h_wheel / 2 - 0.1,
                            ]
                        )
                        + translate
                    )
                    pos_wtl = rotation_theta_phi @ pos_wtl + translate_wtl
                    # pos_wtl += translate_wtl
                    wheel_tl = ptc.Rectangle(
                        pos_wtl,
                        w_wheel,
                        h_wheel,
                        angle=np.rad2deg(delta + phi),
                        color="black",
                    )

                    # wheel top right
                    pos_wtr = np.array([-w_wheel / 2, -h_wheel / 2])
                    translate_wtr = (
                        rotation_phi
                        @ np.array(
                            [
                                center_to_wheels - 0.05,
                                h_car / 2 - h_spoiler - h_wheel / 2 - 0.1,
                            ]
                        )
                        + translate
                    )
                    pos_wtr = rotation_theta_phi @ pos_wtr + translate_wtr
                    wheel_tr = ptc.Rectangle(
                        pos_wtr,
                        w_wheel,
                        h_wheel,
                        angle=np.rad2deg(delta + phi),
                        color="black",
                    )

                    # wheel bottom left
                    pos_wbl = np.array([-w_wheel / 2, -h_wheel / 2])
                    translate_wbl = (
                        -rotation_phi
                        @ np.array(
                            [
                                -center_to_wheels + 0.05,
                                -h_car / 2 + h_spoiler + 3 * h_wheel / 2 + 0.3 + h_body,
                            ]
                        )
                        + translate
                    )
                    pos_wbl = rotation_phi @ pos_wbl + translate_wbl
                    wheel_bl = ptc.Rectangle(
                        pos_wbl, w_wheel, h_wheel, angle=np.rad2deg(phi), color="black"
                    )

                    # wheel bottom right
                    pos_wbr = np.array([-w_wheel / 2, -h_wheel / 2])
                    translate_wbr = (
                        -rotation_phi
                        @ np.array(
                            [
                                center_to_wheels - 0.05,
                                -h_car / 2 + h_spoiler + 3 * h_wheel / 2 + 0.3 + h_body,
                            ]
                        )
                        + translate
                    )
                    pos_wbr = rotation_phi @ pos_wbr + translate_wbr
                    wheel_br = ptc.Rectangle(
                        pos_wbr, w_wheel, h_wheel, angle=np.rad2deg(phi), color="black"
                    )

                    # 7 patches per car so clear only if all cars are drawn
                    if len(self._content[car._trajectory[0]]["ax"].patches) > 7 * (
                        len(self._cars) - 1
                    ):
                        self._content[car._trajectory[0]]["ax"].patches.clear()
                    self._content[car._trajectory[0]]["ax"].add_patch(car_body)
                    self._content[car._trajectory[0]]["ax"].add_patch(front_spoiler)
                    self._content[car._trajectory[0]]["ax"].add_patch(rear_spoiler)
                    self._content[car._trajectory[0]]["ax"].add_patch(wheel_tl)
                    self._content[car._trajectory[0]]["ax"].add_patch(wheel_tr)
                    self._content[car._trajectory[0]]["ax"].add_patch(wheel_bl)
                    self._content[car._trajectory[0]]["ax"].add_patch(wheel_br)

        self._fig.canvas.draw()
        # print("total plotting time {}".format(perf_counter() - start_plotting)) #uncomment to show plotting time


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


def plot_telemetry(
    track, trajectory, steering, motor, yaw, yaw_rate, vx, vy, show_units=False
):
    """Visualize the telemetry data.

    Args:
        track (Track): The track (skidpad or acceleration).
        trajectory (np.ndarray): The trajectory of the car.
        steering (np.ndarray): The steering angle of the car.
        motor (np.ndarray): The motor torque of the car.
        yaw (np.ndarray): The yaw angle of the car (normalized between -pi and pi).
        yaw_rate (np.ndarray): The yaw rate of the car.
        vx (np.ndarray): The longitudinal velocity of the car.
        vy (np.ndarray): The lateral velocity of the car.
    """
    plot = Plot(
        row_nbr=5,
        col_nbr=2,
        mode=PlotMode.DYNAMIC,
        sampling_time=0.1,
        interval=50,
    )

    # get track data
    center_line, widths, right_cones, left_cones = (
        skidpad(0.5) if track == "skidpad" else acceleration_track(0.5)
    )

    # plot track and trajectory
    plot.add_subplot(
        subplot_name="trajectory",
        row_idx=range(4),
        col_idx=0,
        unit="m",
        show_unit=show_units,
        subplot_type=SubplotType.SPATIAL,
        curves={
            "left_cones": {
                "data": left_cones,
                "curve_type": CurveType.STATIC,
                "curve_style": CurvePlotStyle.SCATTER,
                "mpl_options": {"color": "blue", "marker": "^"},
            },
            "right_cones": {
                "data": right_cones,
                "curve_type": CurveType.STATIC,
                "curve_style": CurvePlotStyle.SCATTER,
                "mpl_options": {"color": "blue", "marker": "^"},
            },
            "center_line": {
                "data": center_line,
                "curve_type": CurveType.STATIC,
                "curve_style": CurvePlotStyle.PLOT,
                "mpl_options": {"color": "green"},
            },
            "trajectory": {
                "data": trajectory,
                "curve_type": CurveType.STATIC,
                "curve_style": CurvePlotStyle.PLOT,
                "mpl_options": {"color": "red"},
            },
        },
    )

    # plot steering angle
    plot.add_subplot(
        subplot_name="steering",
        row_idx=0,
        col_idx=1,
        unit="deg",
        show_unit=show_units,
        subplot_type=SubplotType.TEMPORAL,
        curves={
            "steering": {
                "data": steering,
                "curve_type": CurveType.REGULAR,
                "curve_style": CurvePlotStyle.PLOT,
                "options": {"color": "blue", "marker": "o"},
            },
        },
    )

    # plot motor rpm
    plot.add_subplot(
        subplot_name="motor",
        row_idx=1,
        col_idx=1,
        unit="rpm",
        show_unit=show_units,
        subplot_type=SubplotType.TEMPORAL,
        curves={
            "steering": {
                "data": motor,
                "curve_type": CurveType.REGULAR,
                "curve_style": CurvePlotStyle.PLOT,
                "options": {"color": "blue", "marker": "o"},
            },
        },
    )

    # normalize yaw angle between -pi and pi
    yaw = np.mod(yaw + np.pi, 2 * np.pi) - np.pi
    # plot yaw
    plot.add_subplot(
        subplot_name="yaw",
        row_idx=2,
        col_idx=1,
        unit="rad",
        show_unit=show_units,
        subplot_type=SubplotType.TEMPORAL,
        curves={
            "yaw": {
                "data": yaw,
                "curve_type": CurveType.REGULAR,
                "curve_style": CurvePlotStyle.PLOT,
                "options": {"color": "blue", "marker": "o"},
            },
        },
    )

    # plot yaw rate
    plot.add_subplot(
        subplot_name="yaw rate",
        row_idx=3,
        col_idx=1,
        unit="rad",
        show_unit=show_units,
        subplot_type=SubplotType.TEMPORAL,
        curves={
            "yaw rate": {
                "data": yaw_rate,
                "curve_type": CurveType.REGULAR,
                "curve_style": CurvePlotStyle.PLOT,
                "options": {"color": "blue", "marker": "o"},
            },
        },
    )

    # plot longitudinal speed
    plot.add_subplot(
        subplot_name="velocity x",
        row_idx=4,
        col_idx=0,
        unit="m/s",
        show_unit=show_units,
        subplot_type=SubplotType.TEMPORAL,
        curves={
            "velocity": {
                "data": vx,
                "curve_type": CurveType.REGULAR,
                "curve_style": CurvePlotStyle.PLOT,
                "options": {"color": "blue", "marker": "o"},
            },
        },
    )

    # plot lateral speed
    plot.add_subplot(
        subplot_name="velocity y",
        row_idx=4,
        col_idx=1,
        unit="m/s",
        show_unit=show_units,
        subplot_type=SubplotType.TEMPORAL,
        curves={
            "velocity": {
                "data": vy,
                "curve_type": CurveType.REGULAR,
                "curve_style": CurvePlotStyle.PLOT,
                "options": {"color": "blue", "marker": "o"},
            },
        },
    )

    plot.plot(show=True)
