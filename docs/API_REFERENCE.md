# API Reference

In the following you can find a summary of the docstrings of the important classes in the `data_visualization` package.

# `PlotMode`
Enum used to specify the mode of the plot. Available modes are:
- STATIC: classic way of plotting data, all the curves are plotted at once, without any animation.
- DYNAMIC: creates an animated way of displaying data that is already generated and that is provided at the
creation of the plot (e.g. after the simulation you were running has ended).
- LIVE_DYNAMIC: just as the dynamic mode, the live dynamic mode can be used to display animated data. The
difference is that the data does not need to already be generated and can be provided to the `Plot` object
throughout the experiment via a socket communication mechanism.

See [`README.md`](../README.md) for more details.

# `SubplotType`
Enum used to specify the type of subplot. Available types are:
- SPATIAL : the data is plotted on a 2D space.
- TEMPORAL : the data is plotted on a 1D space as a function of time.

See [`README.md`](../README.md) for more details.

# `CurveType`
Enum used to specify the type of curve. Available types are:
- STATIC: the curve is plotted once at the creation of the Plot and in dynamic and live dynamic modes
does not change throughout the animation.
- REGULAR: in static mode the curve is simply displayed, in dynamic and live dynamic modes, the
curve is animated by appending values to it at each iteration.
- PREDICTION: only used in dynamic and live dynamic modes (ignored in static mode), the curve is fully redrawn at
each iteration instead of appending values to it.

See [`README.md`](../README.md) for more details.

# `CurvePlotStyle`
Enum used to specify the type of curve. Available types are:
- STATIC: the curve is plotted once at the creation of the Plot and in dynamic and live dynamic modes
does not change throughout the animation.
- REGULAR: in static mode the curve is simply displayed, in dynamic and live dynamic modes, the
curve is animated by appending values to it at each iteration.
- PREDICTION: only used in dynamic and live dynamic modes (ignored in static mode), the curve is fully redrawn at
each iteration instead of appending values to it.

See [`README.md`](../README.md) for more details.

# `Car`
Class used to represent the car in the plot. The car is represented by a rectangle that is rotated
according to the orientation of the car and whose tires are rotated according to the steering angle.

## `Plot`
This class can be used to plot the evolution of several measures throughout time. A
matplotlib figure is created containing a gridspec on which you can add subplots
taking one or several (contiguous) positions. In these subplots you can add several
curves with a great number of options of customization.

### `Plot.__init__()`
Initializes the plot with an empty Gridspec of size row_nbr x col_nbr and specifies the plot mode and several
important options.

- mode (PlotMode): the mode of the plot. Can be STATIC, DYNAMIC, or LIVE_DYNAMIC
- row_nbr (int): number of rows
- col_nbr (int): number of columns
- figsize (tuple[float, float]: size of the figure (in inches, see matplotlib documentation for more details)
- interval (int): interval between frames in milliseconds, only needed for DYNAMIC and LIVE_DYNAMIC modes,
    ignored in STATIC mode
- sampling_time (float): sampling time used in the experiment, only needed if the temporal subplots need to have
    an x-axis with time instead of number of iteration
- host (str): host of the socket server to which to connect for socket communication, only needed for
    LIVE_DYNAMIC mode, ignored in STATIC and DYNAMIC modes
:type host: str
- port (str): port of the socket server to which to connect for socket communication, only needed for
    LIVE_DYNAMIC mode, ignored in STATIC and DYNAMIC modes
- show_car (bool): boolean to show the car or not
- **kwargs (dict): additional arguments to pass to the ErrorMessageMixin constructor (right now only the verbose
    parameter to display error messages or not for the communication).

### `Plot.add_subplot()`
Adds a new subplot to the plot at a position specified by row_idx and col_idx
that should not be already taken by another subplot. If the position is already
taken, a ValueError is raised.

This method creates the subplot but doesn't draw anything on it. It only checks that the specified data is coherent
(options and data dimensions coherent with the plot mode, subplot type, curve type, etc.) and stores the data
in the _content dictionary. The actual drawing is done in the plot method.
If any incoherence is found, a ValueError is raised.

- subplot_name (str): name of the subplot that will be used as title
- row_idx (Union[slice, int, range]): row indices of the subplot, should be contiguous. If they are not, a ValueError is raised.
:type row_idx:
- col_idx (Union[slice, int, range]): column indices of the subplot, should be contiguous. If they are not, a
  ValueError is raised.
- subplot_type (SubplotType): type of the subplot. Should be either SubplotType.SPATIAL or SubplotType.TEMPORAL. See
    the documentation of the SubplotType enum for more details.
- unit (str): unit of the subplot. Example: "m", "m/s", "rad", "rad/s", "N", "Nm", "W", "V", "A", "C", "F", "Hz"
- show_unit (bool): whether to show the unit of the subplot in the title or not.
- curves (dict): A dictionary of curves of the following format:
     curves={
         "curve_1": {
             "data": data_1,
             "curve_type": CurveType.STATIC,
             "curve_style": CurvePlotStyle.SCATTER,
             "mpl_options": {"color": "red", "marker": "^"},
        },
        "curve_2": {
            "data": data_2,
            "curve_type": CurveType.REGULAR,
            "curve_style": CurvePlotStyle.PLOT,
            "mpl_options": {"color": "blue"},
         },
     }
     The curve types and plot styles could of course change depending on the plot mode.
     The data for each curve should be numpy arrays of the following dimensions:
     - for spatial subplots
     |  | static plot | dynamic plot | live dynamic plot |
     | --- | --- | --- | --- |
     | static curve | (anything, 2) | (anything, 2) | (anything, 2) |
     | regular curve | (N,2) | (N,2) | None at initialization and (2,) at each publish |
     | prediction curve | (N,M,2) | (N,M,2) | None at initialization and (M, 2) at each publish |

     - for temporal subplots
     |  | static plot | dynamic plot | live dynamic plot |
     | --- | --- | --- | --- |
     | static curve | (anything,) | (anything,) | (anything,) |
     | regular curve | (N,) | (N,) | None at initialization and (1,) at each publish |
     | prediction curve | (N,M) | (N,M) | None at initialization and (M,) at each publish |

- car_data_type (Optional[str]): the type of data to link to the car (see class Car).
- car_data_names (Optional[list]): i-th value is the name of the curve containing the data for the data_type attribute
  of the
  `car_id[i]`-th car.
- car_ids (Optional[list]): ids of the car that are concerned by the data of the subplot. Must have same size as
  `car_data_names`.
  See
  bellow for more details. ids to show

### `Plot.plot()`
Plots everything. In static mode, just plots everything once. In dynamic and live dynamic modes, plots the static
curves and then creates an animation based on FuncAnimation from matplotlib.animation.

- show (bool): whether to also call plt.show() at the end
- save_path (Optional[str]): if not None, the path where to save the plot (image file for static mode, video for
  dynamic
  modes).
    Saving a video needs ffmpeg to be installed on the system (see README.md for more details on the installation).


# `Publisher`
