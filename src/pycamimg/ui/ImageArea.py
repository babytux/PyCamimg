#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Thanks to Jack Valmadre.
Please visit: http://jackvalmadre.wordpress.com/2008/09/21/resizable-image-control/
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
    __log__.fatal("It can not import pygtk module. Sure you have installed pygtk?")
    raise e

import gettext
import FactoryControls


class ImageArea(gtk.DrawingArea):
    """
    @summary: Class that manage image.
    """
    def __init__(self, aspect=True, enlarge=False,
                 interp=gtk.gdk.INTERP_NEAREST, backcolor=None,
                 max=(1600, 1200)):
        """
        @summary: Create new image area.
        Parameters:
        aspect -- Maintain aspect ratio?
        enlarge -- Allow image to be scaled up?
        interp -- Method of interpolation to be used.
        backcolor -- Tuple (R, G, B) with values ranging from 0 to 1,
            or None for transparent.
        max -- Max dimensions for internal image (width, height).


        """
        gtk.DrawingArea.__init__(self)
        self.__pixbuf__ = None
        self.connect('expose_event', self.expose)
        self.max = max
        self.backcolor = backcolor
        self.interp = interp
        self.aspect = aspect
        self.enlarge = enlarge
        
    def expose(self, widget, event):
        # Load Cairo drawing context.
        self.context = self.window.cairo_create()
        # Set a clip region.
        self.context.rectangle(
            event.area.x, event.area.y,
            event.area.width, event.area.height)
        self.context.clip()
        # Render image.
        self.draw(self.context)
        return False
    
    def draw(self, context):
        """
        @summary: Draw control.
        @param context: Context of control. 
        """
        # Get dimensions.
        rect = self.get_allocation()
        x, y = rect.x, rect.y
        # Remove parent offset, if any.
        parent = self.get_parent()
        if parent:
            offset = parent.get_allocation()
            x -= offset.x
            y -= offset.y
        # Fill background color.
        if self.backcolor:
            context.rectangle(x, y, rect.width, rect.height)
            context.set_source_rgb(*self.backcolor)
            context.fill_preserve()
        # Check if there is an image.
        if not self.pixbuf:
            return
        width, height = resizeToFit(
            (self.pixbuf.get_width(), self.pixbuf.get_height()),
            (rect.width, rect.height),
            self.aspect,
            self.enlarge)
        x = x + (rect.width - width) / 2
        y = y + (rect.height - height) / 2
        context.set_source_pixbuf(
            self.pixbuf.scale_simple(width, height, self.interp), x, y)
        context.paint()

    def set_from_pixbuf(self, pixbuf):
        """
        @summary: Set image as pixbuf.
        @param pixbuf: Pixbuf that contains image. 
        """
        width, height = pixbuf.get_width(), pixbuf.get_height()
        # Limit size of internal pixbuf to increase speed.
        if not self.max or (width < self.max[0] and height < self.max[1]):
            self.pixbuf = pixbuf
        else:
            width, height = resizeToFit((width, height), self.max)
            self.pixbuf = pixbuf.scale_simple(
                width, height,
                gtk.gdk.INTERP_BILINEAR)
        self.invalidate()
        
    def set_from_file(self, filename):
        """
        @summary: Set image from file.
        @param filename: Filename where image is. 
        """
        self.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(filename))

    def set_from_stock(self, stock):
        """
        @summary: Set image from stock image.
        @param Id stock of the image.: 
        """
        self.set_from_pixbuf(FactoryControls.getPixbufFromStock(stock))

    def invalidate(self):
        """
        @summary: Queue image drawer.
        """
        self.queue_draw()
        
    def getMaxSize(self):
        """
        @summary: Gets max size of picture.
        @retun: Tuple (width, height)
        """
        return self.max

def resizeToFit(image, frame, aspect=True, enlarge=False):
    """
    @summary: Resizes a rectangle to fit within another.
    @param image: A tuple of the original dimensions (width, height).
    @param frame: A tuple of the target dimensions (width, height).
    @param aspect: Maintain aspect ratio?
    @param enlarge: Allow image to be scaled up?
    @return: A tupel with image dimensions (width, height).
    """
    if aspect:
        return scaleToFit(image, frame, enlarge)
    else:
        return stretchToFit(image, frame, enlarge)

def scaleToFit(image, frame, enlarge=False):
    """
    @summary: Scale an image to frame.
    @param image: A tuple of the original dimensions (width, height).
    @param frame: A tuple of the target dimensions (width, height).
    @param enlarge: Allow image to be scaled up?
    @return: A tuple with image dimensions (width, height).  
    """
    image_width, image_height = image
    frame_width, frame_height = frame
    image_aspect = float(image_width) / image_height
    frame_aspect = float(frame_width) / frame_height
    # Determine maximum width/height (prevent up-scaling).
    if not enlarge:
        max_width = min(frame_width, image_width)
        max_height = min(frame_height, image_height)
    else:
        max_width = frame_width
        max_height = frame_height
    # Frame is wider than image.
    if frame_aspect > image_aspect:
        height = max_height
        width = int(height * image_aspect)
    # Frame is taller than image.
    else:
        width = max_width
        height = int(width / image_aspect)
    return (width, height)

def stretchToFit(image, frame, enlarge=False):
    """
    @summary: Adjust image to frame.
    @param image: A tuple of the original dimensions (width, height).
    @param frame: A tuple of the target dimensions (width, height).
    @param enlarge: Allow image to be scaled up?
    @return: A tuple with image dimensions (width, height).  
    """
    image_width, image_height = image
    frame_width, frame_height = frame
    # Stop image from being blown up.
    if not enlarge:
        width = min(frame_width, image_width)
        height = min(frame_height, image_height)
    else:
        width = frame_width
        height = frame_height
    return (width, height)
