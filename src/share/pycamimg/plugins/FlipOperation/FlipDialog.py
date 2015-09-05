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
import FlipOperation.camimgplugin
from FlipOperation import Operation
from pycamimg.ui.ImagePreview import ImagePreview
from pycamimg.util.ImgMeta import ImgMeta

class FlipDialog (gtk.Dialog):
    """
    @summary: Class that manage flip dialog.
    """
    
    __DEFAULT_WINDOW_WIDTH__ = 500
    __DEFAULT_WINDOW_HEIGHT__ = 350
    
    def __init__(self, callback=None, parent=None):
        """
        @summary: Create flip dialog.
        @param callback: Callback that it will do after close dialog.
        @param parent: GtkWindow parent.
        """
        super(FlipDialog, self).__init__()
        
        super(FlipDialog, self).set_title(self.__trans__("Flip/Mirror Images"))
        super(FlipDialog, self).set_flags(gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT)
        super(FlipDialog, self).add_buttons(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                                gtk.STOCK_OK, gtk.RESPONSE_OK)
        
        super(FlipDialog, self).set_transient_for(parent)
        if (parent != None):
            super(FlipDialog, self).set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        else:
            super(FlipDialog, self).set_position(gtk.WIN_POS_CENTER)
        
        # Add signals
        super(FlipDialog, self).connect("response", self.__closeEvent__)
        
        self.__initUI__()
        
        super(FlipDialog, self).set_size_request(self.__DEFAULT_WINDOW_WIDTH__, self.__DEFAULT_WINDOW_HEIGHT__)

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
        return gettext.translation(FlipOperation.camimgplugin.camimgpluginName, __LOCALE_FOLDER__,
                                   languages=[__LANGKEY__], fallback=True).gettext(msg)    
    
    def __initUI__(self):
        """
        @summary: Initialize UI of dialog.
        """
        
        fMain = gtk.Frame()
        lMainFrame = gtk.Label()
        lMainFrame.set_use_markup(True)
        lMainFrame.set_text(self.__trans__("Orientations"))
        fMain.set_label_widget(lMainFrame)
        
        aMainFrame = gtk.Alignment(xalign=0.5, yalign=0.5, xscale=1.0, yscale=1.0)
        aMainFrame.set_padding(0, 0, 12, 0)
        
        self.__chkVertical__ = gtk.CheckButton(label=self.__trans__("Vertical"))
        self.__chkVertical__.set_name("__chkVertical__")
        self.__chkVertical__.set_active(False)
        self.__chkVertical__.connect('toggled', self.__flipChanged__)
        
        self.__chkHorizontal__ = gtk.CheckButton(label=self.__trans__("Horizontal"))
        self.__chkHorizontal__.set_name("__chkHorizontal__")
        self.__chkHorizontal__.set_active(False)
        self.__chkHorizontal__.connect('toggled', self.__flipChanged__)
        
        vBoxFrame = gtk.VBox()
        vBoxFrame.pack_start(self.__chkVertical__, False, False)
        vBoxFrame.pack_start(self.__chkHorizontal__, False, False)

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
            orientation = self.getData()
            if (self.__callback__ != None):
                self.__callback__(self, orientation)

        w.hide()

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
        @return: Orienatation selected.
        """
        orientation = Operation.NONE
        if (self.__chkVertical__.get_active()):
            orientation += Operation.VERTICAL
        elif (self.__chkHorizontal__.get_active()):
            orientation = Operation.HORIZONTAL
        
        return orientation

    def setData(self, item):
        """
        @summary: Set data to dialog.
        @param item: Item to edit. 
        """
        if (not isinstance(item, pycamimg.core.CamItem.CamItem)):
            sMessage = "Orientation must be CamItem"
            __log__.error(sMessage)
            raise TypeError(sMessage)
        
        orientation = Operation.NONE
        if (item != None):
            op = item.getOperation(Operation.OPERATION)
            if (op != None):
                orientation = op.getParameter("orientation")

            self.__setImage__(item)

        while ((orientation < Operation.NONE) and (orientation >= Operation.BOTH)):
            if (orientation < Operation.NONE):
                orientation += Operation.BOTH
            else:
                orientation -= Operation.BOTH
        if (orientation in (Operation.VERTICAL, Operation.BOTH)):
            self.__chkVertical__.set_active(True)
        elif (orientation in (Operation.HORIZONTAL, Operation.BOTH)):
            self.__chkHorizontal__.set_active(True)
        else:
            __log__.debug("There is not check selected.")
            
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
        
    def __flipChanged__(self, toggledButton):
        """
        @summary: Attend toggled event of checkbuttons.
        @param toggledButton: Button that fired event. 
        """
        orientation = Operation.NONE
        if (self.__chkHorizontal__.get_active()):
            orientation += Operation.HORIZONTAL
        if (self.__chkVertical__.get_active()):
            orientation += Operation.VERTICAL
            
        img = self.__img__.copy()
        op = Operation.Flip(orientation=orientation)
        img = op.preview(img)
        self.__refreshImage__(img)
            
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

