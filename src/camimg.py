#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Copyright 2008, 2009, 2010 Hugo Párraga Martín

This file is part of PyCamimg.

PyCamimg is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

PyCamimg is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with PyCamimg.  If not, see <http://www.gnu.org/licenses/>.

"""

import sys
import os.path
import traceback

try:
    import pycamimg.PyCamimg
except IOError:
    print >> sys.stderr, "It can not import pycamimg.PyCamimg. Sure you have installed it."

path = os.path.abspath(os.path.dirname(sys.argv[0]))
os.chdir(path)
preloadedCores = None
if (len(sys.argv) > 1):
    preloadedCores = []
    for count in range(1, len(sys.argv)):
        param = sys.argv[count]
        if (not param.startswith("-")):
            preloadedCores.append(param)
        elif (param.startswith("--") and (param.find("=") == -1)):
            # Parameter without whitespace. Eg. --output=python.py
            # TODO: process parameters
            pass
        else:
            #Parameter with whitespace. Eg. -o python.py
            # TODO: process parameters
            pass
p = None
try:
    sys.path.append(os.path.join(path, "pycamimg"))
    p = pycamimg.PyCamimg.PyCamimg(path, preloadCores=preloadedCores)
except Exception, ex:
    print >> sys.stderr, "An error has occurred. %s" % ex
    traceback.print_exc(file=sys.stderr)
finally:
    if p:
        del p
del path

