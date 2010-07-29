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

from pycamimg.ui import FactoryControls
from pycamimg.ui import UIUtils
from pycamimg.util import ImageUtils

import gettext
import ResizeOperation.camimgplugin

class ResizeDialog (gtk.Dialog):
    """
    @summary: Class that manage resize dialog.
    """

    DEFAULT_DPI = 300

    def __init__(self, callback = None, parent=None):
        """
        @summary: Create new resizeDialog
        @param callback: Callback that it will do after close dialog.
        @param parent: GtkWindow parent.
        """      
        super(ResizeDialog, self).__init__()
        
        super(ResizeDialog, self).set_title(self.__trans__("Resize Images"))
        super(ResizeDialog, self).set_flags(gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT)
        super(ResizeDialog, self).add_buttons(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                              gtk.STOCK_OK, gtk.RESPONSE_OK)
        
        super(ResizeDialog, self).set_transient_for(parent)
        if (parent != None):
            super(ResizeDialog, self).set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        else:
            super(ResizeDialog, self).set_position(gtk.WIN_POS_CENTER)
        
        # Add signals
        super(ResizeDialog, self).connect("response", self.__closeResizeEvent__)
        
        self.__initUI__()

        # Set callback that will be executing when the dialog closes with
        # accept response
        self.__callback__ = callback

        # Init source size in pixels and dpi
        self.__srcSize__ = (0, 0)
        self.__srcDpi__ = self.DEFAULT_DPI #Default dpi

        # Init size dictionary
        self.__lastSizes__ = {
            ImageUtils.PERCENT : (0, 0),
            ImageUtils.PIXEL : (0, 0),
            ImageUtils.CM : (0, 0)
            }
        __log__.debug("Size dictionary initialized")

    def __trans__(self, msg):
        """
        @summary: Translate msg.
        @param msg: str within message. 
        @return: str translated.
        """
        return gettext.translation(ResizeOperation.camimgplugin.camimgpluginName, __LOCALE_FOLDER__, 
                                   languages=[__LANGKEY__], fallback = True).gettext(msg)

    def __initUI__(self):
        """
        @summary: Initialize UI of dialog.
        """
        tBox = gtk.Table(rows=4, columns=2, homogeneous=False)
        tBox.set_col_spacings(5)
        tBox.set_row_spacings(5)
        
        # Radio buttons.
        self.__rbPixel__ = gtk.RadioButton(label=self.__trans__("Pixels"))
        self.__rbPixel__.set_name("__rbPixel__")
        self.__rbPixel__.set_active(True)
        self.__rbPixel__.connect("toggled", self.__changeScaleEvent__)
        
        self.__rbCM__ = gtk.RadioButton(group=self.__rbPixel__, label=self.__trans__("CM"))
        self.__rbCM__.set_name("__rbCM__")
        self.__rbCM__.set_active(False)
        self.__rbCM__.connect("toggled", self.__changeScaleEvent__)
        
        self.__rbPercentage__ = gtk.RadioButton(group=self.__rbPixel__, label=self.__trans__("Percentaje"))
        self.__rbPercentage__.set_name("__rbPercentage__")
        self.__rbPercentage__.set_active(False)
        self.__rbPercentage__.connect("toggled", self.__changeScaleEvent__)
        
        hBoxChoice = gtk.HBox()
        hBoxChoice.pack_start(self.__rbPixel__, False, False)
        hBoxChoice.pack_start(self.__rbCM__, False, False)
        hBoxChoice.pack_start(self.__rbPercentage__, False, False)
        
        tBox.attach(hBoxChoice, 0, 2, 0, 1, yoptions=0)
        tBox.attach(gtk.HSeparator(), 0, 2, 1, 2, yoptions=0)
        
        # Inputs.
        hBoxWidth = gtk.HBox()
        self.__spWidth__ = gtk.SpinButton(climb_rate=1.00)
        self.__spWidth__.set_name("__spWidth__")
        self.__spWidth__.set_increments(1.00, 10.00)
        self.__spWidth__.set_range(0.00, sys.maxint)
        self.__spWidth__.set_numeric(True)
        self.__spWidth__.set_editable(True)
        self.__spWidth__.set_update_policy(gtk.UPDATE_IF_VALID)
        self.__spWidth__.connect("focus-out-event", self.__valueChangedEvent__)
        
        hBoxWidth.pack_start(gtk.Label(str=self.__trans__("Width")), False, False)
        hBoxWidth.pack_start(self.__spWidth__, False, True)
        tBox.attach(hBoxWidth, 0, 1, 2, 3, yoptions=gtk.FILL, xoptions=0)
        
        hBoxHeight = gtk.HBox()
        self.__spHeight__ = gtk.SpinButton(climb_rate=1.00)
        self.__spHeight__.set_name("__spHeight__")
        self.__spHeight__.set_increments(1.00, 10.00)
        self.__spHeight__.set_range(0.00, sys.maxint)
        self.__spHeight__.set_numeric(True)
        self.__spHeight__.set_editable(True)
        self.__spHeight__.set_update_policy(gtk.UPDATE_IF_VALID)
        self.__spHeight__.connect("focus-out-event", self.__valueChangedEvent__)
        
        hBoxHeight.pack_start(gtk.Label(str=self.__trans__("Height")), False, False)
        hBoxHeight.pack_start(self.__spHeight__, False, True)
        tBox.attach(hBoxHeight, 0, 1, 3, 4, yoptions=gtk.FILL, xoptions=0)
    
        self.__tbLock__ = gtk.ToggleButton()
        self.__tbLock__.set_active(True)
        self.__tbLock__.connect("toggled", self.__lockToggledEvent__)
        imgLock = gtk.Image()
        UIUtils.setImageToButton(self.__tbLock__, os.path.join(__ICONS_FOLDER__, "lock.png"), doGObject=False)
        
        tBox.attach(self.__tbLock__, 1, 2, 2, 4, xoptions=0, yoptions=0)
        
        self.get_child().pack_start(tBox, True, True)
        
        tBox.show_all()

    def __calculateSize__ (self, srcScale, size):
        """
        @summary: Calculate size of the dictionary.
        @param srcScale: Scale of the size.
        @param size: Size of a image.
        """
        __log__.debug("Scale: %s" % srcScale)
        if (srcScale == ImageUtils.PERCENT):
            self.__lastSizes__[ImageUtils.PERCENT] = size
            self.__lastSizes__[ImageUtils.PIXEL]= (
                self.__srcSize__[0] * (float(size[0]) / 100), 
                self.__srcSize__[1] * (float(size[1]) / 100))
            self.__lastSizes__[ImageUtils.CM] = ImageUtils.pixelToCm(
                self.__lastSizes__[ImageUtils.PIXEL],
                self.__srcDpi__)
        elif (srcScale == ImageUtils.PIXEL):
            self.__lastSizes__[ImageUtils.PIXEL]= size
            self.__lastSizes__[ImageUtils.CM] = ImageUtils.pixelToCm(
                size, 
                self.__srcDpi__)

            if (self.__srcSize__[0] != 0):
                self.__lastSizes__[ImageUtils.PERCENT] = (
                    (float(size[0]) / self.__srcSize__[0]) * 100, 
                    (float(size[1]) / self.__srcSize__[1]) * 100)
            else:
                __log__.debug("Source size is 0. It can not possible calculate other scales.")
                self.__lastSizes__[ImageUtils.PERCENT] = (0, 0)

        elif (srcScale == ImageUtils.CM):
            self.__lastSizes__[ImageUtils.CM]= size
            self.__lastSizes__[ImageUtils.PIXEL] = ImageUtils.cmToPixel(
                size, 
                self.__srcDpi__)

            if (self.__srcSize__[0] != 0):
                self.__lastSizes__[ImageUtils.PERCENT] = (
                    (float(size[0]) / self.__srcSize__[0]) * 100, 
                    (float(size[1]) / self.__srcSize__[1]) * 100)
            else:
                __log__.debug("Source size is 0. It can not possible calculate other scales.")
                self.__lastSizes__[ImageUtils.PERCENT] = (0, 0)
        else:
            __log__.error("Scale unknown")

    def __setActiveRadios__(self, active):
        """
        @summary: Set if pixel and cm are actived.
        @param active: True to enable radio buttons. 
        """
        self.__rbPixel__.set_sensitive(active)
        self.__rbCM__.set_sensitive(active)

    def __setConditionsSpins__(self, scale):
        """
        @summary: Sets conditions in spinbuttons.
        @param scale: Scate to establish conditions. 
        """
        if (scale == ImageUtils.PERCENT):
            self.__spWidth__.set_range(0.00, sys.maxint)
            self.__spWidth__.set_increments(1.00, 10.00)

            self.__spHeight__.set_range(0.00, sys.maxint)
            self.__spHeight__.set_increments(1.00, 10.00)
        elif (scale == ImageUtils.CM):
            self.__spWidth__.set_range(0.00, sys.maxint)
            self.__spWidth__.set_increments(0.10, 1.00)

            self.__spHeight__.set_range(0.00, sys.maxint)
            self.__spHeight__.set_increments(0.10, 1.00)
        elif (scale == ImageUtils.PIXEL):
            self.__spWidth__.set_range(0.00, sys.maxint)
            self.__spWidth__.set_increments(1.00, 10.00)

            self.__spHeight__.set_range(0.00, sys.maxint)
            self.__spHeight__.set_increments(10.00, 10.00)
        else:
            __log__.error("Scale unknown")
            
    def __printSize__(self, size):
        """
        @summary: Print size into ui.
        @param size: Tuple with size (width, height)
        """
        self.__spWidth__.set_value(float(size[0]))
        self.__spHeight__.set_value(float(size[1]))
        
        
    def __valueChangedEvent__(self, sp, event=None):
        """
        @summary: Handle value-changed event of SpinButtons.
        @param sp: SpinButton to handle.
        @param event: That throw the method.  
        """
        bIsLock = True
        upWidth = False
        upHeight = False
        newWidth = 0
        newHeight = 0
        diff = 1
        scale = ImageUtils.PERCENT

        bIsLock = self.__tbLock__.get_active()
        scale = self.getCurrentScale()

        if (sp.get_name() == "__spWidth__"):
            newWidth = sp.get_value()
            if (self.__lastSizes__[scale][0] != 0):
                diff = float(newWidth) / float(self.__lastSizes__[scale][0])
        elif (sp.get_name() == "__spHeight__"):
            newHeight = sp.get_value()
            if (self.__lastSizes__[scale][1] != 0):
                diff = float(newHeight) / float(self.__lastSizes__[scale][1])

        #Update values only when a change has ocurred
        if (diff != 1):
            if (scale == ImageUtils.PIXEL):
                newWidth = round(newWidth)
                newHeight = round(newHeight)

            # When lock button is set
            if (bIsLock):
                if (newWidth != 0):
                    newHeight = float(self.__lastSizes__[scale][1]) * diff
                    upHeight = True
                elif (newHeight != 0):
                    newWidth = float(self.__lastSizes__[scale][0]) * diff
                    upWidth = True
            else:
                if (newWidth != 0):
                    newHeight = float(self.__lastSizes__[scale][1])
                else:
                    newWidth = float(self.__lastSizes__[scale][0])
                       
        
            #Update last size of a scale
            self.__calculateSize__(scale, (newWidth, newHeight))
            if (upWidth):
                self.__spWidth__.set_value(newWidth)
            if (upHeight):
                self.__spHeight__.set_value(newHeight)

    def __closeResizeEvent__(self, w, res):
        """
        @summary: Handle response of resize dialog.
        @param w: GtkDialog that raise the event.
        @param res: Response associated with the event.  
        """
        if (res == gtk.RESPONSE_OK):
            print "Response"
            
            width, height, unit = self.getData()

            if (width <= 0):
                sMessage = self.__trans__("Width must be getter than 0")
                __log__.info(sMessage)
                FactoryControls.getMessage(
                    sMessage, 
                    title=self.__trans__("Wrong width"), 
                    type=gtk.MESSAGE_ERROR,
                    parent = self)
            if (height <= 0):
                sMessage = self.__trans__("Height must be getter than 0")
                __log__.info(sMessage)
                FactoryControls.getMessage(
                    sMessage, 
                    title=self.__trans__("Wrong height"), 
                    type=gtk.MESSAGE_ERROR,
                    parent = self)
    
            if ((self.__callback__ != None) and (width > 0) and (height > 0)):
                self.__callback__(self, width, height, unit)

        w.hide()

    def __lockToggledEvent__(self, button):
        """
        @summary: Handle toggle event of lock button.
        @param button: ToggledButton associated with the event. 
        """
        if (self.__rbPercentage__.get_active()):
            size = self.__lastSizes__[ImageUtils.PERCENT]
            if (size[0] < size[1]):
                size[1] = size[0]
            elif (size[1] < size[0]):
                size[0] = size[1]
            
            self.__calculateSize__(ImageUtils.PERCENT, size)

    def __changeScaleEvent__(self, button):
        """
        @summary: Handle toggle event of scale radio buttons.
        @param button: New RadioButton selected. 
        """
        if (button.get_name() == "__rbPercentage__"):
            if (not self.__tbLock__.get_active()):
                self.__tbLock__.set_active(True)
            self.__tbLock__.set_sensitive(False);
            scale = ImageUtils.PERCENT
        elif (button.get_name() == "__rbCM__"):
            self.__tbLock__.set_sensitive(True);
            scale = ImageUtils.CM
        elif (button.get_name() == "__rbPixel__"):
            self.__tbLock__.set_sensitive(True);
            scale = ImageUtils.PIXEL
        else:
            __log__.error("Unknown button raised event.")
            return

        self.__printSize__(self.__lastSizes__[scale])
        self.__setConditionsSpins__(scale)

    def setResponseCallback(self, callback):
        """
        @summary: Sets callback that will call when dialog close.
        @param callback: Function reference. 
        @note: callback model: callback (dialog: gtk.Dialog, width: float, height: float, unit:int)
        """
        self.__callback__ = callback

    def getData(self):
        """
        @summary: Gets data of dialog.
        @return: tuple with (width, height, scale)
        """
        width = self.__spWidth__.get_value()
        height = self.__spHeight__.get_value()
        unit = ImageUtils.PIXEL
        if (self.__rbPixel__.get_active()):
            unit = ImageUtils.PIXEL
        elif (self.__rbCM__.get_active()):
            unit = ImageUtils.CM
        elif (self.__rbPercentage__.get_active()):
            unit = ImageUtils.PERCENT
        return (width, height, unit)

    def setData(self, width, height, unit, srcSize=None):
        """
        @summary: Set data to dialog.
        @param with: With of a image.
        @param height: Height of a image.
        @param unit: Sacale of the width and height.
        @param srcSize: Tuple with width and height in pixels.
        @raise TypeError: Raise when height, width or unit are not int or float. 
        """
        if (not isinstance(width, float) and not isinstance(width, int)):
            sMessage = "Width must be float or integer number"
            __log__.error(sMessage)
            raise TypeError(sMessage)
        if (not isinstance(height, float) and not isinstance(height, int)):
            sMessage = "Height must be float or integer number"
            __log__.error(sMessage)
            raise TypeError(sMessage)
        if (not isinstance(unit, int)):
            sMessage = "Unit must be PIXEL(0) or CM(1)or PERCENT(2)"
            __log__.error(sMessage)
            raise TypeError(sMessage)
        elif ((unit < ImageUtils.PIXEL) or (unit > ImageUtils.PERCENT)) :
            sMessage = "Unit must be PIXEL(0), CM(1) or PERCENT(2)"
            __log__.error(sMessage)
            raise TypeError(sMessage)

        radio = None
        if (unit == ImageUtils.PIXEL):
            radio = self.__rbPixel__
            if (srcSize != None):
                self.__srcSize__ = srcSize
            else:
                self.__srcSize__ = (float(width), float(height))
            self.__setActiveRadios__(True)
        elif (unit == ImageUtils.CM):
            radio = self.__rbCM__
            if (srcSize != None):
                self.__srcSize__ = srcSize
            else:
                self.__srcSize__ = ImageUtils.cmToPixel(
                    (float(width), float(height)), 
                    self.__srcDpi__)
            self.__setActiveRadios__(True)
        elif (unit == ImageUtils.PERCENT):
            
            radio = self.__rbPercentage__
            self.__setActiveRadios__(True)
        else:
            __log__.error("Scale unknown")

        if (radio != None):
            radio.set_active(True)
        
        self.__printSize__((float(width), float(height)))
        self.__calculateSize__(unit, (float(width), float(height)))
        self.__setConditionsSpins__(unit)

    def getCurrentScale(self):
        """
        @summary: Gets current scale.
        @return: Integer with current scale
        """
        # Get current scale
        if (self.__rbPercentage__.get_active()):
            scale = ImageUtils.PERCENT
        elif (self.__rbPixel__.get_active()):
            scale = ImageUtils.PIXEL
        elif (self.__rbCM__.get_active()):
            scale = ImageUtils.CM
        else:
            __log__.error("Any radio button are not selected")

        return scale