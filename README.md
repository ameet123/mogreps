## netCDF4 Parsing

### Change:

+ 7/20
used the meshgrid approach
```python
mesh(var_name)
```

+ 7/19
A simpler approach to reduce added

This uses `tile` and `repeat`

A generic method to write any variable to a CSV
Usage:
```python
flatten_any('air_temperature')
```

### Objective:

Parse a `netCDF4` format file into more manageable and human readable format for further processing.

### Input
The file is in a binary format called, `netCDF4`. This format collects multi-dimensional data into a
single file. The structure is a hierachical one and is as follows,
File ->
1. Groups: this is optional and there is always one group present, `rootgrp`
    2. Dimensions: These are fields with values or in other words, *columns* of data.
    3. Variables: This is akin to a database `Table`. A variable is composed of multiple dimensions.

### Variables:
As described above, a variable is a table. The implementation format for this variable is a `numpy` array.
A given file may already have *variables* created in it by the author.
New variables can be created on the fly based on the dimensions available in the file as well.

### Variable Data [ a numpy array ]:

The data in the variable is stored as a numpy array. However the data is *masked*.
In order to reduce storage, numpy provides `masked arrays`, in which the values missing can be filled in
with a `fill_value` or large number of constant values can be replaced with a small value to conserve space.

To extract the data from the *Variable*, we need to unmask the numpy array and fill it with the appropriate
fill value.

### Dimensions, Indexing and Joins:

Although the data is multi-dimensional, it is not stored in a single *Variable*.
For e.g., let's consider **air_temperature**.
This has four dimensions - *time, pressure, latitude, longitude -> temperature*
If we look at the numpy array, it will be a 4-dimensional array with dims,
`Shape: (4,2,528,421)`
However, all the data will apear to be temperature. There will be no trace of a date, pressure or latitude.
These other dimensions/fields are to be *deduced* from other *Variables* based on `indexing` in numpy.

Continuing with the same example, we know that the first dimension of size 4 is time.
Then we look inside the file for a variable called `time` and extract the numpy array from there.
This will be a single dimensional array with 4 values of dates. These are the dates which match the
indexes 0,1,2,3 from the air_temperature numpy array.
So if we are looking at the first *row* of air_temp[0],
then it pertains to the first date from the `time` array.

### Implementation

The specific approach reduces the dimensions from the main variable and appends the other dimension values.
Therefore, a 4-D air_temp variable will be converted to a 2-D array with rows and 5 columns.

This is then converted to a `Pandas Dataframe` and written to a `csv` file.