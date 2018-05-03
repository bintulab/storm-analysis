#!/usr/bin/env python
"""
Calculates offset, variance and gain for each pixel of
a sCMOS camera. The input files are in the form that
is generated by calibrate.py program in the folder
hal4000/hamamatsu/ of the STORM-Control project which
is available here:

http://zhuang.harvard.edu/software.html

The units of the results are:
offset - adu
gain - adu / e-
variance - adu ^ 2

Hazen 12/17
"""

import matplotlib
import matplotlib.pyplot as pyplot
import numpy
import os
import sys

def cameraCalibration(scmos_files, show_fit_plots = True, show_mean_plots = True):
    n_points = len(scmos_files)
    all_means = False
    all_vars = False

    assert(len(scmos_files) > 1), "Need at least two calibration files."

    offset = None
    variance = None
    for i, a_file in enumerate(scmos_files):
        print(i, "loading", a_file)

        # Load data.
        #
        # Originally this was a list of length 3. Later we added a 4th element
        # which is a dictionary containing some information about the camera ROI.
        #
        all_data = numpy.load(a_file)
        if (len(all_data) == 3):
            [data, x, xx] = all_data
        else:
            [data, x, xx, roi_dict] = all_data
            if (i == 0):
                print("Calibration ROI info:")
                for key in sorted(roi_dict):
                    print(key, roi_dict[key])
                print()

        # Originally data was just the number of frames, later it was changed to
        # an array containing the mean intensity in each frame.
        #
        if (data.size == 1):
            frames = data[0]
            mean_var = 0.0

        else:
            frames = data.size
            if (i > 0):
                mean_var = numpy.var(data)
            else:
                mean_var = 0.0
                
            print(a_file, mean_var)
            
            if show_mean_plots:
                xv = numpy.arange(frames)
                pyplot.figure()
                pyplot.plot(xv, data)
                pyplot.xlabel("Frame")
                pyplot.ylabel("Mean Intensity (ADU)")
                pyplot.show()
        
        x = x.astype(numpy.float64)
        xx = xx.astype(numpy.float64)
        file_mean = x/float(frames)
        file_var = xx/float(frames) - file_mean * file_mean - mean_var

        if not isinstance(all_means, numpy.ndarray):
            all_means = numpy.zeros((x.shape[0], x.shape[1], n_points))
            all_vars = numpy.zeros((x.shape[0], x.shape[1], n_points))

        if (i > 0):
            all_means[:,:,i] = file_mean - offset
            all_vars[:,:,i] = file_var - variance
        else:
            offset = file_mean
            variance = file_var

    gain = numpy.zeros((all_means.shape[0], all_means.shape[1]))

    nx = all_means.shape[0]
    ny = all_means.shape[1]
    for i in range(nx):
        for j in range(ny):
            gain[i,j] = numpy.polyfit(all_means[i,j,:], all_vars[i,j,:], 1)[0]
            if (((i*ny+j) % 1000) == 0):
                print("pixel", i, j,
                      "offset {0:.3f} variance {1:.3f} gain {2:.3f}".format(all_means[i,j,0],
                                                                            all_vars[i,j,0],
                                                                            gain[i,j]))

    if show_fit_plots:
        print("")
        for i in range(5):
            pyplot.figure()

            data_x = all_means[i,0,:]
            data_y = all_vars[i,0,:]
            fit = numpy.polyfit(data_x, data_y, 1)

            print(i, "gain {0:.3f}".format(fit[0]))
            pyplot.scatter(data_x,
                           data_y,
                           marker = 'o',
                           s = 2)

            xf = numpy.array([0, data_x[-1]])
            yf = xf * fit[0] + fit[1]
            
            pyplot.plot(xf, yf, color = 'blue')
            pyplot.xlabel("Mean Intensity (ADU).")
            pyplot.ylabel("Mean Variance (ADU).")
            
            pyplot.show()


    return [offset, variance, gain]


if (__name__ == "__main__"):

    import argparse

    parser = argparse.ArgumentParser(description = 'sCMOS camera calibration.')

    parser.add_argument('--results', dest='results', type=str, required=True,
                        help = "The name of the numpy format file to save the results in.")
    parser.add_argument('--cal', nargs = "*", dest='cal', type=str, required=True,
                        help = "Storm-control format calibration files, in order dark, light1, light2, ...")

    args = parser.parse_args()

    if os.path.exists(args.results):
        print("calibration file already exists, please delete before proceeding.")
        exit()
    
    [offset, variance, gain] = cameraCalibration(args.cal)
    
    numpy.save(args.results, [offset, variance, gain, 1])
    

#
# The MIT License
#
# Copyright (c) 2017 Zhuang Lab, Harvard University
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
