# Copyright Lihui Cui

import os
import numpy as np
import matplotlib.pyplot as plt
import struct
import collections
import sys

default_args = collections.OrderedDict()
default_args['cmd'] = ""
default_args["testname"] = "help"
default_args["testfile"] = ""

def load_imgfile(options):
    testfile = os.path.normpath(options.infile)
    print testfile
    h = options.height
    w = options.width
    import tempfile
    #from scipy import misc
    #img = misc.read(filename)

    histfile = os.path.join(tempfile.gettempdir(),'imginfo.pkl')
    #print histfile

    import pickle
    imginfo = None
    try:
        with open(histfile, 'rb') as f:
            imginfo = pickle.load(f)
    except:
        imginfo = {'img-w': 192,
                   'img-h': 256,
                   'img-dtype': 'float32',
                   'img-scale': 1}

    data = np.fromfile(testfile, options.dtype)
    if options.imgtype == "yuv":
        y, u, v = np.split(data, 3)
        y = np.reshape(y, (h, w))
        u = np.reshape(u, (h, w))
        v = np.reshape(v, (h, w))
        data = np.dstack((y, u, v))
    elif options.imgtype == "bayer":
        data = np.reshape(data, (h, w))
        data = np.dstack((data, data, data))
    else :
        ch = data.shape[0]/(w*h)
        data = np.reshape(data, (h, w, ch))

    with open(histfile, 'wb') as f:
        pickle.dump(imginfo, f, pickle.HIGHEST_PROTOCOL)

    return data

def showimg(data, options):
    img = data 
    if options.imgtype == "yuv":
        yuv2rgb = np.array([[1.0,           0,      1.13983],
                            [1.0,    -0.39465,     -0.58060],
                            [1.0,     2.03211,            0]])
        img = np.dot(data, yuv2rgb.T)

    plt.imshow(img)
    plt.show()

def imgval(data, options):
    roi = [int(x) for x in options.roi.split(',')]
    if len(roi) != 4:
        print "Error: wrong ROI(%s)" % options.roi
        return

    x = roi[0]
    y = roi[1]
    w = roi[2]
    h = roi[3]
    print "Image values at pos(%d, %d), size %dx%d" % (x, y, w, h)
    print data[y:y+h,x:x+w]

if __name__ == "__main__":
    from optparse import OptionParser

    parser = OptionParser(usage="usage: %prog [options]",
                          version="%prog 1.0")
    parser.add_option("-i", "--input",
                      dest="infile",
                      default="",
                      metavar="FILE",
                      help="file name for the input")

    parser.add_option("-c", "--cmd",
                      dest="cmd",
                      default="imgval",
                      choices=['show', 'imgval'],
                      help="Command to run")
  
    parser.add_option("-W", "--width",
                      dest="width",
                      default=1032,
                      type="int",
                      metavar="NUMBER",
                      help="width of image")
    parser.add_option("-H", "--height",
                      dest="height",
                      default="1288",
                      type="int",
                      metavar="NUMBER",
                      help="height of image")
    parser.add_option("-t", "--type",
                      dest="imgtype",
                      default="rgb",
                      choices=['rgb', 'yuv', 'bayer'],
                      help="image type(rgb, yuv, bayer)")

    parser.add_option("-s", "--scale",
                      dest="scale",
                      default="1",
                      type="int",
                      metavar="NUMBER",
                      help="Scale to the input image")

    parser.add_option("-d", "--dtype",
                      dest="dtype",
                      default="float32",
                      choices=['float32', 'uint8', 'uint16', 'uint32', 'int32'],
                      help="Data type(uint8-32, float32)")

    parser.add_option("-r", "--roi",
                      dest="roi",
                      default="30, 30, 4, 4",
                      help='Region of interests, Please put values in "", e.g "10, 10, 4, 4"')
    
    (options, args) = parser.parse_args()
    print options

    if not os.path.exists(options.infile):
        print "Error, input file does not exist!!!"
        #parser.print_help()
        exit(1)

    tests = {
            "imgval"    : imgval,
            "show"      : showimg,
            }

    data = load_imgfile(options)
    print data.shape, data.dtype

    func = tests.get(options.cmd, imgval)
    func(data, options)

