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
import os
import os.path
import pycamimg
import logging
if hasattr(sys, "frozen"):
    logging._srcfile = os.path.join("logging", "__init__.pyo")
try:
    __log__ = logging.getLogger(pycamimg.LogName)
except:
    __log__ = logging.getLogger()

try:
    import pygtk
    if (not (sys.platform == "win32")):
        pygtk.require('2.0')
    import gtk, gobject
except Exception, e:
    __log__.fatal("It can not import pygtk module. Sure you have installed pygtk?" )
    raise e

import gettext
from ImageArea import ImageArea

class ImagePreview ():
    """
    @summary: Class that manage flip dialog.
    """
    def __init__(self, showFrame=True):
        """
        @summary: Create image preview control.
        @param showFrame: True if it wants show frame 
        """
        self.__fPreview__ = None
        self.__im__ = ImageArea(enlarge=True)
        self.__im__.set_from_stock(gtk.STOCK_MISSING_IMAGE)
        self.__lPreview__ = None
        if (showFrame):
            self.__fPreview__ = gtk.Frame()
            self.__lPreview__ = gtk.Label()
            self.__lPreview__.set_use_markup(True)
            self.__lPreview__.set_text(_("Preview"))
            self.__fPreview__.set_label_widget(self.__lPreview__)
            
            aPreview = gtk.Alignment(xalign=0.5, yalign=0.5, xscale=1.0, yscale=1.0)
            aPreview.set_padding(0, 0, 0, 0)

            aPreview.add(self.__im__)
            self.__fPreview__.add(aPreview)
    
    def getTitleFrame(self):
        """
        @summary: Gets title of frame if frame exists.
        @return: str within title.
        """
        if (self.__lPreview__ != None):
            return self.__lPreview__.get_text()
        else:
            return ""
     
    def getControl(self):
        """
        @summary: Gets control to show.
        @return: If it is gonna show frame, it gets gtk.Frame control.
                Else it gets gtk.Image control.
        """
        if (self.__fPreview__ != None):
            return self.__fPreview__
        else:
            return self.__im__
    
    def getImageControl(self):
        """
        @summary: Gets control that shows image.
        @return: ImageArea control.
        """
        return self.__im__