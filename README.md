# data_visualization

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A simple [matplotlib](https://matplotlib.org/)-based utility library for visualizing data in control simulations and
more.

The main features of this library are grouped in the `Plot` class which represents a matplotlib window with multiple
subplots displaying data.
You can add several types of data in each subplot and can easily create animated plots and save them to a video file.
Please refer to section [Usage](#usage) for more details.

# Installation
To simply use the library, install it with
```bash
pip install git+https://github.com/EPFL-RT-Driverless/data_visualization.git@v2.0.0#egg=data_visualization
```
To develop the package, follow the instructions of the
[Notion guide](https://www.notion.so/epflrt/How-to-work-at-the-EPFL-Racing-Team-c9d1f06a81854c628b38d4107eac624e).

# Usage

The `Plot` class is the main class of the library. It represents a matplotlib window with multiple _subplots_.
It is first constructed as an empty grid (leveraging matplotlib's
[`Gridspec`](https://matplotlib.org/stable/api/_as_gen/matplotlib.gridspec.GridSpec.html)) that the user can
populate with the `add_subplot` method in a declarative fashion. This method declares the _curves_ that each subplot
contains. This hierarchy _plot > subplot> curve_ is represented in the following image:
![plot-subplot-curve](plot_subplot_curve.png)

In data_visualization, you can highly customize all the data you specify. Most of the customization options are
described by four enum classes : `PlotMode`, `SubplotType`, `CurveTyple` and `CurvePlotType`. Thy are described in
the following sections.

## `PlotMode`
This option is specified at the plot level and defines three different operating modes:
- **Static** : classic way of plotting data, all the curves are plotted at once, without any animation. All
  the data to plot is specified at the plot creation (e.g. after the simulation you were running has ended). Probably
  the most useful in a lot of cases.
- **Dynamic** : creates an animated way of displaying data that is already generated and that is provided at the
  creation of the plot (e.g. after the simulation you were running has ended). It is mostly useful for saving a
  video of the animation.
[//]: # (TODO: add ref to below)
- **Live dynamic** : just as the dynamic mode, the live dynamic mode can be used to display animated data. The
  difference is that the data does not need to already be generated and can be provided to the `Plot` object
  throughout the experiment via a socket communication mechanism. This is useful for displaying data in real-time
  during a simulation.
  The advantage of using sockets is that the data can be generated on a different machine than the one that
  displays the data. This is useful for example when you want to display real time data from a running car.
  More details can be found in...

## `SubplotType`
There are 2 subplots types that are specified in the call to `add_subplot` and that describe the nature of the data
to be
displayed:
- **spatial** : the data is plotted on a 2D space. This is useful for displaying a XY trajectory for example.
- **temporal** : the data is plotted on a 1D space as a function of time. This is useful for displaying an arbitrary
  value (e.g. speed, steering angle, ...) as a function of time.

## `CurveType`
A curve can be of 3 types :
- **static** : the curve is plotted once at the creation of the Plot and in dynamic and live dynamic modes
  does not change throughout the animation. This is useful for plotting static obstacles like cones or bounds on
  temporal values.
- **regular** : in static mode the curve is simply displayed, in dynamic and live dynamic modes, the
  curve is animated by appending values to it at each iteration. This is useful for plotting the trajectory of the
  car and the evolution of any value over time.
- **prediction** : only used in dynamic and live dynamic modes (ignored in static mode), the curve is fully redrawn at
  each iteration instead of appending values to it. This is useful for plotting predicted trajectories of a car (e.g.
  provided by an MPC controller) that change at each iteration without being related to the one from the previous
  iteration.

> Note: Be careful to make the distinction between a _static curve_ and a _static plot_.

[//]: # (TODO : add dimensions of the matrices provided )


### Curve plot types
These types refer to the matplotlib plotting functions, they are defined in the `CurvePlotType` enum :
- plot
- scatter : Scatter cannot be used for dynamic plots.
- step
- semilogx
- semilogy
- loglog
> Note: Scatter cannot currently be used for dynamic and live dynamic plots.

[//]: # (TODO: Add details on the communication protocol.)

### Build a video from a dynamic plot
When calling the function `plot`, after initializing the plot, you can pass the argument `save_path` to save the video
at the specified path. This requires a FFMpeg encoder to be installed on your machine. If it is not follow this
[tutorial](https://holypython.com/how-to-save-matplotlib-animations-the-ultimate-guide/) (paragraph "2) Installing FFMpeg").
And you can find the download link [here](https://www.ffmpeg.org/download.html).

If you don't want to install FFMpeg you can use another writer for matplotlib : PillowWriter. To do so, just comment and
uncomment the lines in the call of `self._anim.save` in the function `plot` of the `Plot` class (`plot.py`). The drawback
is the format: it only allows to save the video in .gif format.

### Plotting a simple representation of the car
You have the possibility to plot a simple representation of the car. To do so, you need to pass the argument `show_car=true`
while initializing the plot.

The class `Car` is used to know which data to use :
- `_trajectory : string` : the trajectory of the car.
- `_orientation : string` : the orientation angle of the car.
- `_steering : string` : the steering angle of the car.

These attributes are set while adding a subplot. The argument `car_data_type : string` is used to precise which attribute
to set. The argument `car_data_names : list[string]` is used to precise which curve to use for the data. The argument
`car_ids : list[int]` is used to precise which car is concerned by the data.

To add a new car you simply need to pass the next id in the argument `car_ids` and the list of cars will be updated automatically.

And a attribute `_show_car` that stays `False` until the `_trajectory` attribute is set. This attribute is the only one
necessary to plot the car.

# Examples
You can find examples in the [`tests`](tests) folder. For dynamic and static plots, you can read the `test_plot.py`
file, or `test_telemetry.py`. For live dynamic plots, you can read both files in
[tests/test_live_dynamic](tests/test_live_dynamic) folder.

# Implementation details (for developers)

`ErrorMessageMixin` is inherited in most classes to standardize error messages output.
