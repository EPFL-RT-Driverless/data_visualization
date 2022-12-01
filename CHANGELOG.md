# v1.1.0
added telemetry visualization templates and tests to demo the visualization from mock car data.

added full testing for static and dynamic plots.

added the car plotting feature.

added documentation for the visualization module (see the `DOC.md` file).

fixed bugs on prediction curves.

fixed a bug one video creation.

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
