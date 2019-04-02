# Urban-Climatology-tools
A set of Python scripts to calculate various surface parameters. I intend to extend and upgrade it in the future...

I am developing a set of Python scripts, that can be used in urban climatology research and urban planning.
Most of the scripts need a digital surface model (DSM) and some other settings as input.

# Prerequisites

OsGeo GDAL/OGR Python package is needed to use the provided scripts. You can use pip or other package managers to install it.

# Usage

The (in their current form) are intended to use in command line. You can create a .bat/ .sh file with the arguments You want to run the scripts with.

# Continuous H/W ratio calculation:

Calculates H/W value for every pixel of the input DSM in a direction of 360 degrees according to the arguments given. Can have a long processing time depending on the size of the input DSM. Returns a raster file as an output.

Use the continuousHWcalculation.py with the following arguments:
- Path to the raster DSM data
- Height threshold value - setting the minimum canyon height You are looking for. H/W will not be calculated if height difference is below this value
- Degree steps - the algorithm goes around a full circle, starting in the northern direction (0 degrees); the given value will be used as a difference between the angles included by the search directions
- Pixel steps - the runtime of the script can be very long, depending on the size of the DSM. If you want a less detailed, but still accurate output, set this value over 1. The algorithm will only calculate for every n-th pixels value. Since we are calculating a 2 dimensional output, the effect of pixel step on runtime is exponential. E.g.: use a pixel step value of 3 to achieve 9 times les runtime
- Frame value - This will exclude the x number of pixels (given as frame value) along the edges of the data from the calculation. Pixels around the edges won't be accurate enough, since they are not surrounded by other pixels from every direction
- Path of the output folder
- Name of the output file


# Vector based H/W calculation:

Uses vector data of roads to find possible canyons in the DSM. If canyon is found H/W ratio is calculated perpendicular to road direction

Use the vectorHWcalculation.py with the following arguments:

- Path to the raster DSM data
- Path to the vector data, containing the roads
- Height threshold value - Setting the minimum canyon height You are looking for. H/W will not be calculated if height difference is below this value
- Frame value - This will exclude the x number of pixels (given as frame value) along the edges of the data from the calculation. Pixels around the edges won't be accurate enough, since they are not surrounded by other pixels from every direction
- Path of the output folder
- Name of the output file
