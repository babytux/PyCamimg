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

import gettext
import RenameOperation.camimgplugin
from pycamimg.ui import FactoryControls

COUNTER = "%COUNTER%"

class RenameDialog (gtk.Dialog):
    """
    @summary: Defines rename dialog.
    """
    
    def __init__(self, numberOfItems, callback=None, parent=None):
        """
        @summary: Creates new rename dialog.
        @param numberOfItems: Number of items to rename.
        @param callback: Callback that it will do after close dialog.
        @param parent: GtkWindow parent.
        """
        super(RenameDialog, self).__init__()
        
        super(RenameDialog, self).set_title(self.__trans__("Rename Images"))
        super(RenameDialog, self).set_flags(gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT)
        super(RenameDialog, self).add_buttons(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                              gtk.STOCK_OK, gtk.RESPONSE_OK)
        
        super(RenameDialog, self).set_transient_for(parent)
        if (parent != None):
            super(RenameDialog, self).set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        else:
            super(RenameDialog, self).set_position(gtk.WIN_POS_CENTER)
        
        # Add signals
        super(RenameDialog, self).connect("response", self.__closeEvent__)
        
        self.__nItems__ = numberOfItems
        
        self.__initUI__()
        
        # Set callback that will be executing when the dialog closes with
        # accept response
        self.__callback__ = callback
    
    def __trans__(self, msg):
        """
        @summary: Translate msg.
        @param msg: str within message. 
        @return: str translated.
        """
        return gettext.translation(RenameOperation.camimgplugin.camimgpluginName, __LOCALE_FOLDER__,
                                   languages=[__LANGKEY__], fallback=True).gettext(msg)
     
    def __initUI__(self):
        """
        @summary: Initialize UI of dialog.
        """
        self.__vBoxMain__ = gtk.VBox()
        
        self.__initUIName__()
        self.__initUIOptions__()
        
        self.get_child().pack_start(self.__vBoxMain__, True, True)
        self.__vBoxMain__.show_all()
        
    def __initUIName__(self):
        """
        @summary: Initialize name part of ui.
        """
        self.__txtPrefix__ = gtk.Entry()
        self.__txtSuffix__ = gtk.Entry()
        
        self.__spInitialCount__ = gtk.SpinButton(climb_rate=1.00)
        self.__spInitialCount__.set_name("__spInitialCount__")
        self.__spInitialCount__.set_increments(1.00, 10.00)
        self.__spInitialCount__.set_range(0.00, sys.maxint)
        self.__spInitialCount__.set_numeric(True)
        self.__spInitialCount__.set_editable(True)
        self.__spInitialCount__.set_update_policy(gtk.UPDATE_IF_VALID)
        self.__spInitialCount__.set_value(0.00)

        self.__chkEnableCount__ = gtk.CheckButton(label=self.__trans__("Enabled"))
        self.__chkEnableCount__.set_active(True)
        self.__chkEnableCount__.connect("toggled", self.__enabledCountEvent__)
        self.__chkEnableCount__.set_sensitive(self.__nItems__ == 1)
        
        fEnableCount = gtk.Frame()
        fEnableCount.set_label_widget(self.__chkEnableCount__)
        fEnableCount.add(self.__spInitialCount__)
        
        table = gtk.Table(rows=3, columns=3, homogeneous=False)
        table.set_col_spacings(10)
        table.set_row_spacings(4)
        
        table.attach(gtk.Label(str=self.__trans__("Prefix")), 0, 1, 0, 1, yoptions=0, xoptions=0)
        table.attach(self.__txtPrefix__, 1, 3, 0, 1, yoptions=0, xoptions=gtk.FILL)
        
        table.attach(gtk.Label(str=self.__trans__("Initial number")), 0, 1, 1, 2, yoptions=0, xoptions=0)
        table.attach(fEnableCount, 1, 3, 1, 2, yoptions=0, xoptions=gtk.FILL)
        
        table.attach(gtk.Label(str=self.__trans__("Suffix")), 0, 1, 2, 3, yoptions=0, xoptions=0)
        table.attach(self.__txtSuffix__, 1, 3, 2, 3, yoptions=0, xoptions=gtk.FILL)
        
        aName = gtk.Alignment(xalign=0.5, yalign=0.5, xscale=1.0, yscale=1.0)
        aName.set_padding(0, 0, 12, 0)
        aName.add(table)
        
        lbl = gtk.Label(str=("<b>%s</b>" % self.__trans__("Name")))
        lbl.set_use_markup(True)
        
        fName = gtk.Frame()
        fName.set_label_widget(lbl)
        fName.add(aName)
        
        self.__vBoxMain__.pack_start(fName, False, True)
        
    def __initUIOptions__(self):
        """
        @summary: Initialize options part of ui.
        """
        self.__chkFillNumber__ = gtk.CheckButton(label=self.__trans__("Fill number"))
        self.__chkFillNumber__.set_active(True)
        self.__chkFillNumber__.connect("toggled", self.__chkFillNumberToggledEvent__)
        
        self.__rbAuto__ = gtk.RadioButton(label=self.__trans__("Auto"))
        self.__rbAuto__.set_name("__rbAuto__")
        self.__rbAuto__.set_active(True)
        
        self.__rbCustom__ = gtk.RadioButton(group=self.__rbAuto__, label=self.__trans__("Custom"))
        self.__rbCustom__.set_name("__rbCustom__")
        self.__rbCustom__.set_active(False)
        self.__rbCustom__.connect("toggled", self.__rbCustomToggledEvent__)
        
        self.__spFillNumber__ = gtk.SpinButton(climb_rate=1.00)
        self.__spFillNumber__.set_name("__spFillNumber__")
        self.__spFillNumber__.set_increments(1.00, 10.00)
        self.__spFillNumber__.set_range(0.00, 100)
        self.__spFillNumber__.set_numeric(True)
        self.__spFillNumber__.set_editable(True)
        self.__spFillNumber__.set_update_policy(gtk.UPDATE_IF_VALID)
        self.__spFillNumber__.set_value(0.00)
        
        hBoxCustom = gtk.HBox()
        hBoxCustom.pack_start(gtk.Label(str=self.__trans__("Digits")), False, False)
        hBoxCustom.pack_start(self.__spFillNumber__, False, True)
        
        vBoxFillNumber = gtk.VBox()
        vBoxFillNumber.pack_start(self.__rbAuto__, False, False)
        vBoxFillNumber.pack_start(self.__rbCustom__, False, False)
        vBoxFillNumber.pack_start(hBoxCustom, False, True)
        
        fFillNumber = gtk.Frame()
        fFillNumber.set_label_widget(self.__chkFillNumber__)
        fFillNumber.add(vBoxFillNumber)
        
        eOptions = gtk.Expander(label="<b>%s</b>" % self.__trans__("Options"))
        eOptions.set_use_markup(True)
        eOptions.add(fFillNumber)

        self.__vBoxMain__.pack_start(eOptions, False, True)

    def __enabledCountEvent__(self, b):
        """
        @summary: Handle add enable count check toggled.
        @param b: GtkButton associated. 
        """
        self.__spInitialCount__.set_sensitive(self.__chkEnableCount__.get_active())

    def __closeEvent__(self, w, res):
        """
        @summary: Handle response from rename dialog.
        @param w: GtkDialog that raise event.
        @param res: Response that it is associated with the event.
        @return: False when an error occurred  
        """
        if (res == gtk.RESPONSE_OK):
            sPattern = self.getFormat()
            initial = self.getInitialNumber()
            
            if (self.__callback__ != None):
                __log__.debug("There is a callback. Throwing it.")
                self.__callback__(self, sPattern, initial)
        
        w.hide()

    def __chkFillNumberToggledEvent__(self, b):
        """
        @summary: Handle checkbutton fill number toggled.
        @param b: GtkButton associated with the event. 
        """
        self.__chkFillNumber__.get_active()
        self.__rbAuto__.set_sensitive(self.__chkFillNumber__.get_active())
        self.__rbCustom__.set_sensitive(self.__chkFillNumber__.get_active())
        self.__spFillNumber__.set_sensitive(self.__chkFillNumber__.get_active()
                                             and self.__rbCustom__.get_active())

    def __rbCustomToggledEvent__(self, b):
        """
        @summary: Handle both radio events.
        @param b: RadioButton associated with the event.
        """
        self.__spFillNumber__.set_sensitive(self.__rbCustom__.get_active())

    def getFormat(self):
        """
        @summary: Get current format.
        @return: str within format
        """
        sFormat = self.__txtPrefix__.get_text()
        if (self.__chkEnableCount__):
            sFillFormat = "%d"
            if (self.__chkFillNumber__.get_active()):
                number = 1
                if (self.__rbCustom__.get_active()):
                    number = self.__spFillNumber__.get_value_as_int()
                elif (self.__rbAuto__.get_active()):
                    number = len("%d" % self.__nItems__)
                
                sFillFormat = "%%0%dd" % number 
            
            sFormat += sFillFormat
        
        sFormat += self.__txtSuffix__.get_text()
        return sFormat
        

    def getInitialNumber(self):
        """
        @summary: Gets initial number.
        @return: int with initial number.
        """
        return self.__spInitialCount__.get_value_as_int()

    def setResponseCallback(self, callback):
        """
        @summary: Sets callback that will call when dialog close.
        @param callback: Function reference. 
        @note: callback model: callback (dialog: gtk.Dialog, format: str, initialNumber: int)
        """
        self.__callback__ = callback
