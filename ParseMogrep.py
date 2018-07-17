import numpy as np
import numpy.ma as ma
from netCDF4 import Dataset
from datetime import date, timedelta


class ParseMogrep(object):
    def log(self, print_str):
        if self.verbose:
            print print_str

    def __init__(self, file="data/prods_op_mogreps-uk_20130101_03_00_003.nc", verbose=False):
        self.verbose = verbose
        self.log("Processing netCDF file:{}".format(file))

        self.rootgrp = Dataset(file, "r", format="NETCDF4")
        self.vars = self.rootgrp.variables
        # get lattitude
        self.long = self.get_np_array_unmasked('grid_longitude')
        self.lat = self.get_np_array_unmasked('grid_latitude')
        self.time = self.get_time()
        self.pressure0 = self.get_np_array_unmasked('pressure_0')

    def get_time(self):
        """
        convert hours since 1970-1-1 to regular datetime object
        :param time_array:
        :return: np arra of datetime
        """
        t = self.get_np_array_unmasked('time')
        converter = np.vectorize(lambda x: date(1970, 1, 1) + timedelta(hours=x))
        y = converter(t)
        self.log("Time array shape:{}".format(y.shape))
        return y

    def get_np_array_unmasked(self, var):
        a = self.vars[var][:].filled(self.vars[var][:].fill_value)
        self.log("Shape of {} => {}".format(var, a.shape))
        return a

    def get3d_from_4d(self, name, row, col, third, second):
        air_temp = self.get_np_array_unmasked(name)
        self.log("Total size of records in {}:{} Shape:{}".format(name, air_temp.size, air_temp.shape))
        # Flatten
        w = None
        for j in range(air_temp.shape[0]):
            # This is 4th dim
            w1 = self.get2d_from3d(air_temp[j], row, col, third)
            # get second array val
            second_arr = np.full((w1.shape[0], 1), second[j])
            w1 = np.concatenate((w1, second_arr), axis=1)
            if w is None:
                w = w1
            else:
                w = np.concatenate((w, w1))
        return w

    def parse_airtemp(self):
        return self.get3d_from_4d('air_temperature', self.lat, self.long, self.pressure0, self.time)

    def get_2d_array(self, arr, r, c):
        """
        convert a 2D array by appending additional attributes for each element from r and c
        :param arr:
        :param r:
        :param c:
        :return:
        """
        w = None
        for i in range(arr.shape[0]):
            rv = np.full((arr[i].shape[0], 1), r[i])
            z = np.concatenate((arr[i].reshape(-1, 1), c.reshape(-1, 1), rv), axis=1)
            if w is None:
                w = z
            else:
                w = np.concatenate((w, z))
        return w

    def get2d_from3d(self, arr3, row, col, third_dim_array):
        """

        :param arr3: this is a 3D array
        :param row:
        :param col:
        :param third_dim_array: this is 1-D array matching rows with arr3
        :return:
        """
        x = None
        for i in range(arr3.shape[0]):
            x1 = self.get_2d_array(arr3[i], row, col)
            # Here get hte pressure(i.e. 3rd dim) and concatenate
            third_array = np.full((x1.shape[0], 1), third_dim_array[i])
            x1 = np.concatenate((x1, third_array), axis=1)
            if x is None:
                x = x1
            else:
                x = np.concatenate((x, x1))
        return x


if __name__ == "__main__":
    mog = ParseMogrep()
    flat = mog.parse_airtemp()
    print("Shape:{} Size={}".format(flat.shape, flat.size))
