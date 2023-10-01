# v1.1.3

removed pinned dependencies for matplotlib and scipy and refactored some commented out code

# v1.1.2

- added `COLCON_IGNORE` file to ignore this package in colcon builds (for brains repo)
- replaced `np.float` by `np.float32` or `np.float64` to avoid deprecation warnings

# v1.1.1

:bug: commented out Kamil's template because it used an old and imcompatible version of tdb 

# v1.1.0

## :sparkles: Enhancements
- Created extensive documentation in [`README.md`](README.md) and [`API_REFERENCE.md`](docs/API_REFERENCE.md), and examples
  in [`examples/`](examples/).
- Added the car plotting feature.
- Added full test suite for static and dynamic plots. Most of them are visual for the moment, but we plan on adding
  more headless tests that could run in CI.
- Added telemetry visualization templates and tests to demo the visualization from mock car data.

## :bug: Bug fixes
- In temporal subplots, the prediction curves were not correctly connected to regular curves on the x-axis. Now they
  are.
- fixed a bug in video creation with ffmpeg.
- fixed the car orientation that sometimes wasn't changed.

# v1.0.5

:bug: fixed bugs with Live Dynamic modes and save

Spatial curves were not displayed correctly in live dynamic mode
because of a wrong call to np.append().
Now using FFMpegWriter to save animations to mp4 format

# v1.0.4

fixed bug with _redrawn_artists (it was called even in Static mode)

# v1.0.3

dynamic visualization optimization

# v1.0.2

Fixed import of git deps in `setup.py`

# v1.0.1

Re-added `fsds_client` as dependency

# v1.0.0

updated everything to match `python_boilerplate` v2.0.1
