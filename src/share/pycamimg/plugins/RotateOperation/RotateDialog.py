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
    __log__.fatal("It can not import pygtk module. Sure you have installed pygtk?")
    raise e

from pycamimg.ui import FactoryControls
import gettext
import RotateOperation.camimgplugin
from RotateOperation import Operation
from pycamimg.ui.ImagePreview import ImagePreview
from pycamimg.util.ImgMeta import ImgMeta

class RotateDialog (gtk.Dialog):
    """
    @summary: Class that manage rotate dialog.
    """
    
    __DEFAULT_WINDOW_WIDTH__ = 500
    __DEFAULT_WINDOW_HEIGHT__ = 350
    
    def __init__(self, callback=None, parent=None):
        """
        @summary: Create rotation dialog.
        @param callback: Callback that it will do after close dialog.
        @param parent: GtkWindow parent.
        """
        super(RotateDialog, self).__init__()
        
        super(RotateDialog, self).set_title(self.__trans__("Rotate Images"))
        super(RotateDialog, self).set_flags(gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT)
        super(RotateDialog, self).add_buttons(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                                gtk.STOCK_OK, gtk.RESPONSE_OK)
        
        super(RotateDialog, self).set_transient_for(parent)
        if (parent != None):
            super(RotateDialog, self).set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        else:
            super(RotateDialog, self).set_position(gtk.WIN_POS_CENTER)
        
        # Add signals
        super(RotateDialog, self).connect("response", self.__closeEvent__)
        super(RotateDialog, self).set_size_request(self.__DEFAULT_WINDOW_WIDTH__, self.__DEFAULT_WINDOW_HEIGHT__)        
        
        self.__initUI__()

        # Set callback that will be executing when the dialog closes with
        # accept response
        self.__callback__ = callback
        
        self.__img__ = None
        self.__item__ = None
    
    def __trans__(self, msg):
        """
        @summary: Translate msg.
        @param msg: str within message. 
        @return: str translated.
        """
        return gettext.translation(RotateOperation.camimgplugin.camimgpluginName, __LOCALE_FOLDER__,
                                   languages=[__LANGKEY__], fallback=True).gettext(msg)    
    
    def __initUI__(self):
        """
        @summary: Initialize UI of dialog.
        """
        
        fMain = gtk.Frame()
        lMainFrame = gtk.Label()
        lMainFrame.set_use_markup(True)
        lMainFrame.set_text(self.__trans__("Select one option"))
        fMain.set_label_widget(lMainFrame)
        
        aMainFrame = gtk.Alignment(xalign=0.5, yalign=0.5, xscale=1.0, yscale=1.0)
        aMainFrame.set_padding(0, 0, 12, 0)
        
        self.__rb0Degrees__ = gtk.RadioButton(label=self.__trans__("0º"))
        self.__rb0Degrees__.set_name("__rb0Degrees__")
        self.__rb0Degrees__.set_active(True)
        self.__rb0Degrees__.connect('toggled', self.__rotationChanged__)
        
        self.__rb90Degrees__ = gtk.RadioButton(group=self.__rb0Degrees__, label=self.__trans__("90º"))
        self.__rb90Degrees__.set_name("__rb90Degrees__")
        self.__rb90Degrees__.set_active(False)
        self.__rb90Degrees__.connect('toggled', self.__rotationChanged__)
        
        self.__rb180Degrees__ = gtk.RadioButton(group=self.__rb0Degrees__, label=self.__trans__("180º"))
        self.__rb180Degrees__.set_name("__rb180Degrees__")
        self.__rb180Degrees__.set_active(False)
        self.__rb180Degrees__.connect('toggled', self.__rotationChanged__)
        
        self.__rb270Degrees__ = gtk.RadioButton(group=self.__rb0Degrees__, label=self.__trans__("270º"))
        self.__rb270Degrees__.set_name("__rb270Degrees__")
        self.__rb270Degrees__.set_active(False)
        self.__rb270Degrees__.connect('toggled', self.__rotationChanged__)
        
        self.__rbCustomDegrees__ = gtk.RadioButton(group=self.__rb0Degrees__, label=self.__trans__("Custom"))
        self.__rbCustomDegrees__.set_name("__rbCustomDegrees__")
        self.__rbCustomDegrees__.set_active(False)
        self.__rbCustomDegrees__.connect("toggled", self.__customToggledEvent__)
        
        self.__spCustom__ = gtk.SpinButton(climb_rate=1.00)
        self.__spCustom__.set_name("__spCustom__")
        self.__spCustom__.set_increments(1.00, 15.00)
        self.__spCustom__.set_range(0.00, 360.00)
        self.__spCustom__.set_numeric(True)
        self.__spCustom__.set_editable(True)
        self.__spCustom__.set_update_policy(gtk.UPDATE_IF_VALID)
        self.__spCustom__.set_value(0.00)
        self.__spCustom__.set_sensitive(False)
        
        self.__bUpdatePreview__ = gtk.Button(stock=gtk.STOCK_REFRESH)
        self.__bUpdatePreview__.set_name("__bUpdatePreview__")
        self.__bUpdatePreview__.connect("clicked", self.__updateImage__)
        self.__bUpdatePreview__.set_sensitive(False)
        
        hBoxCustom = gtk.HBox()
        hBoxCustom.set_spacing(5)
        hBoxCustom.pack_start(self.__rbCustomDegrees__, False, True)
        hBoxCustom.pack_start(self.__spCustom__, False, True)
        hBoxCustom.pack_start(self.__bUpdatePreview__, False, True)
        
        vBoxFrame = gtk.VBox()
        vBoxFrame.pack_start(self.__rb0Degrees__, False, False)
        vBoxFrame.pack_start(self.__rb90Degrees__, False, False)
        vBoxFrame.pack_start(self.__rb180Degrees__, False, False)
        vBoxFrame.pack_start(self.__rb270Degrees__, False, False)
        vBoxFrame.pack_start(hBoxCustom, False, True)
        
        aMainFrame.add(vBoxFrame)
        fMain.add(aMainFrame)
        
        self.__iPreview__ = ImagePreview()
        
        hBox = gtk.HBox()
        hBox.set_spacing(2)
        hBox.pack_start(self.__iPreview__.getControl(), True, True)
        hBox.pack_start(fMain, True, True)
        
        self.get_child().pack_start(hBox, True, True)
        hBox.show_all()
        
    def __closeEvent__(self, w, res):
        """
        @summary: Handle response of rotate dialog.
        @param w: GtkDialog that raise event.
        @param res: Response associated with the event. 
        """
        if (res == gtk.RESPONSE_OK):
            degrees = self.getData()
            if (degrees == -1):
                FactoryControls.getMessage(self.__trans__("There is not valid degrees selected.\nPlease select correct degrees"),
                                           title=self.__trans__("Rotate"),
                                           type=gtk.MESSAGE_ERROR,
                                           parent=self)
                return gtk.FALSE
            
            if (self.__callback__ != None):
                self.__callback__(self, degrees)

        w.hide()

    def __customToggledEvent__(self, b):
        """
        @summary: Handle rCustom toggled event.
        @param b: RadioButton associated with the event. 
        """
        self.__spCustom__.set_sensitive(self.__rbCustomDegrees__.get_active())
        self.__bUpdatePreview__.set_sensitive(self.__rbCustomDegrees__.get_active())
        self.__rotationChanged__(b)

    def setResponseCallback(self, callback):
        """
        @summary: Sets callback that will call when dialog close.
        @param callback: Function reference. 
        @note: callback model: callback (dialog: gtk.Dialog, degrees: int)
        """
        self.__callback__ = callback

    def getData(self):
        """
        @summary: Get data from dialog.
        @return: Degrees selected. -1 = Error.
        """
        degrees = 0
        if (self.__rb0Degrees__.get_active()):
            degrees = 0
        elif (self.__rb90Degrees__.get_active()):
            degrees = 90
        elif (self.__rb180Degrees__.get_active()):
            degrees = 180
        elif (self.__rb270Degrees__.get_active()):
            degrees = 270
        elif (self.__rbCustomDegrees__.get_active()):
            degrees = self.__spCustom__.get_value_as_int()
        else:
            __log__.warning("There is not a radio button selected.")
            degrees = -1
        
        return degrees
    
    def setData(self, item):
        """
        @summary: Set data to dialog.
        @param item: Item to edit. 
        """
        if (not isinstance(item, pycamimg.core.CamItem.CamItem)):
            sMessage = "item must be CamItem"
            __log__.error(sMessage)
            raise TypeError(sMessage)
        
        degrees = 0
        if (item != None):
            op = item.getOperation(Operation.OPERATION)
            if (op != None):
                degrees = op.getParameter("degrees")

            self.__setImage__(item)
            
        self.__setDataDegrees__(degrees)

    def __setDataDegrees__(self, rotation):
        """
        @summary: Set data to dialog.
        @param rotation: Initial degrees 
        """
        if (not isinstance(rotation, int)):
            sMessage = "Rotation must be integer number"
            __log__.error(sMessage)
            raise TypeError(sMessage)

        while ((rotation < 0) and (rotation >= 360)):
            if (rotation < 0):
                rotation += 360
            else:
                rotation -= 360
        radio = None
        if (rotation == 0):
            radio = self.__rb0Degrees__
        elif (rotation == 90):
            radio = self.__rb90Degrees__
        elif (rotation == 180):
            radio = self.__rb180Degrees__
        elif (rotation == 270):
            radio = self.__rb270Degrees__ 
        else:
            radio = self.__rbCustomDegrees__ 
            self.__spCustom__.set_value(float(rotation))
            
        if (radio != None):
            radio.set_active(True)
        else:
            __log__.warning("There is not radiobutton selected.")

    def __rotationChanged__(self, toggledButton):
        """
        @summary: Attend toggled event of checkbuttons.
        @param toggledButton: Button that fired event. 
        """
        degrees = 0     
        degrees = self.getData()
        img = self.__img__.copy()
        op = Operation.Rotate(degrees=degrees)
        img = op.preview(img)
        self.__refreshImage__(img)
        
    def __updateImage__(self, b):
        """
        @summary: Attend update button event.
        @param b: Button that fire the event. 
        """
        degrees = self.getData()
        img = self.__img__.copy()
        op = Operation.Rotate(degrees=degrees)
        img = op.preview(img)
        self.__refreshImage__(img)

    def __setImage__(self, item):
        """
        @summary: Sets image into image control.
        @param item: CamItem to set as image. 
        """
        im = self.__iPreview__.getImageControl()
        self.__item__ = item
        self.__item__.refreshThumbnail(im.getMaxSize()[1])
        self.__img__ = self.__item__.doPreview()
        meta = None
        self.__refreshImage__(self.__img__)

    def __refreshImage__(self, img):
        """
        @summary: Refresh image on ImageArea.
        """
        if ((img != None) and (self.__item__ != None)):
            meta = ImgMeta(self.__item__.getPath(), image=img)
            im = self.__iPreview__.getImageControl()
            if (meta != None):
                pb = meta.getIcon(rescale=100.0, maxHeight=im.getMaxSize()[1])
                im.set_from_pixbuf(pb)
            else:
                __log__.warning("It could not retrieve metadata from item. %s" % self.__item__.getPath())
        else:
            __log__.debug("Img or Item is None. It can not refresh image.")

