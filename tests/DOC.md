# Doc for the data_visualization package

A simple tool based on [matplotlib](https://matplotlib.org/) for visualizing data in control simulations and more. The 
main principle is to build a matplotlib window with multiple plots showing some data. 
The data can be temporal or spatial, and the plots can be static or dynamic. This window is 
of type `Plot` and is a grid of subplots.
errorMessageMixin is inherited to handle better error messages. 

### Installation
Make sure that the requirements (see requirements.txt, requirements_dev.txt) are installed.

### Plotting modes
There are 3 plotting modes :
- Static : classic way of plotting data, all the curves are plotted at once.
- Dynamic : see dynamic section.
- Live dynamic : see live dynamic section.

These types are defined in the `PlotMode` enum, with the attribute `mode` of the `Plot` class.

### Subplots types
There are 2 subplots types :
- spatial : the data is plotted on a 2D space.
- temporal : the data is plotted on a 1D space as a function of time.

These types are defined in the `SubplotType` enum, it needs to be specified during the creation creation of a subplot
(use function `add_subplot` of the `Plot` class).

### Curves types
The curve can be of 3 types :
- static : the curve is plotted all at once whenever the plot mode.
- regular : the curve follows the plot mode (static or dynamic).
- prediction : used for dynamic plots, the curve is fully redrawn at each iteration. The data
for this curve is a list of lists of points. That way at each redrawing a different list is used.

These types are defined in the `CurveType` enum, it needs to be specified during the creation of a curve.
That is when calling `add_subplot` (see below).

### Curve plot types
These types refer to the matplotlib plotting functions, they are defined in the `CurvePlotType` enum :
- plot
- scatter : Scatter cannot be used for dynamic plots.
- step
- semilogx
- semilogy
- loglog

### Declare a plot
To declare a plot, you need to create a `Plot` object. It takes 3 necessary arguments :
- `mode` : the PlotMode enum value of the plot.
- `row_nbr` : the number of rows in the grid.
- `col_nbr` : the number of columns in the grid.
Other arguments are optional :
- `sampling_time` `(optional)`: sampling time used in the experiment, only needed if the temporal subplots need to have an x axis 
with time instead of number of iterations.
- `interval` `(optional)` : the interval, in milliseconds, between each frame in dynamic (or live dynamic) plot, only needed if 
the plot mode is dynamic or live dynamic.
- `figsize` `(optional)` : the size of the matplotlib figure, in inches.
- `host` `(optional)` : the host of the plot, only used if the plot mode is live dynamic.
- `port` `(optional)` : the port of the plot, only used if the plot mode is live dynamic.
- Some `kwargs` that are passed to the `ErrorMessageMixin` class and to the socket for live dynamic.

### Add a subplot
To add a subplot to the plot, you need to call the `add_subplot` function of the `Plot` object. Here are the details
of the arguments :
- `subplot_name` : the name of the subplot.
- `row_idx` : the row index of the subplot in the grid.
- `col_idx` : the column index of the subplot in the grid.
- `subplot_type` : the type of the subplot, see `SubplotType` enum.
- `unit` : the unit of the data to be plotted.
- `show_unit` : boolean, if True the unit is shown in the title of the subplot.
- `curves` : a dictionary of curves to be plotted in the subplot, see below for more details :
    - a `string` : the key and name of the curve.
    - a `dict` : a nested dictionary describing the curve (Make sure to **respect the names**) :
        - `"data"` : the data to be plotted, a list of points. The dimensions depend on the subplot type :
            - spatial : 2D points, of shape (n, 2).
            - temporal : 1D points, of shape (n, 1).
            - and for a curve of type prediction, the shape must be (m, n, 1 or 2) where m is the number of lists of points.
        - `"curve_type"` : the type of the curve, see `CurveType` enum.
        - `"curve_style"` : the style of the curve, see `CurvePlotType` enum.
        - `"mlp_options"` : options to be passed to matplotlib in the plotting function; it is a dictionary.
- `car_data_type : string` : the type of data to link to the car (see class Car).
- `car_data_names : list[string]` : i-th value is the name of the curve containing the data for the data_type attribute of the 
`car_id[i]`-th car.
- `car_ids : list[int]` : ids of the car that are concerned by the data of the subplot. Must have same size as `car_data_names`. See 
bellow for more details.
        
### Dynamic plots
Dynamic mode can be used to show in real time the evolution of some data. These data should be already computed. When 
initializing the subplot. It can also be used to create a video of the evolution of the data. To do so, you need to call 
??

### Live dynamic plots
Live dynamic mode can be used to show some data while they are being computed. The data is sent to the plot through network.
Hence, it can be used to plot some data computed on another machine. 

_Add details on the protocol._

### Examples
You can find examples in the tests folder. For dynamic and static plots, you can read the `test_plot.py` file, or 
`test_telemetry.py`. For live dynamic plots, you can read both files in tests/test_live_dynamic folder.

### Build a video from a dynamic plot
When calling the function `plot`, after initializing the plot, you can pass the argument `save_path` to save the video 
at the specified path. The methods needs FFMpeg encoder to be installed on your machine. If it is not follow this 
[tutorial](https://holypython.com/how-to-save-matplotlib-animations-the-ultimate-guide/) (paragraph "2) Installing FFMpeg").
And you can find the download link [here](https://www.ffmpeg.org/download.html).

I you don't want to install FFMpeg you can use another writer for matplotlib : PillowWriter. To do so, just comment and 
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