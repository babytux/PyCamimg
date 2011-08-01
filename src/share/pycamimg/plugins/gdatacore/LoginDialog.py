#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Copyright 2011 Hugo Párraga Martín

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
import gdatacore.camimgplugin
import gettext

class LoginDialog (gtk.Dialog):
    """
    @summary: Class that manage google data authentication dialog.
    """
    __DEFAULT_WINDOW_WIDTH__ = 400
    __DEFAULT_WINDOW_HEIGHT__ = 250
    
    def __init__(self, parent=None, callback=None):
        """
        @summary: Create new authentication dialog.
        @param parent: GtkWindow parent.
        """
        super(LoginDialog, self).__init__()
        
        import gdatacore.Session
        self.__session__ = gdatacore.Session.Session()
        
        super(LoginDialog, self).set_title(self.__trans__("Google Login"))
        super(LoginDialog, self).set_flags(gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT)
        super(LoginDialog, self).add_buttons(gtk.STOCK_OK, gtk.RESPONSE_OK, gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        
        super(LoginDialog, self).set_transient_for(parent)
        if (parent != None):
            super(LoginDialog, self).set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        else:
            super(LoginDialog, self).set_position(gtk.WIN_POS_CENTER)
        
        # Add signals
        super(LoginDialog, self).connect("response", self.__closeEvent__)
        super(LoginDialog, self).set_size_request(self.__DEFAULT_WINDOW_WIDTH__, self.__DEFAULT_WINDOW_HEIGHT__)
        
        self.__initUI__()
        self.__callback__ = callback


    def __trans__(self, msg):
        """
        @summary: Translate msg.
        @param msg: str within message. 
        @return: str translated.
        """
        return gettext.translation(gdatacore.camimgplugin.camimgpluginName, __LOCALE_FOLDER__, 
                                   languages=[__LANGKEY__], fallback = True).gettext(msg)

    def __initUI__(self):
        """
        @summary: Initialize ui.
        """
        self.__tbUserName__ = gtk.Entry()
        
        self.__tbPwd__ = gtk.Entry()
        
        tData = gtk.Table(rows=2, columns=2)
        
        tData.attach(gtk.Label(self.__trans__("Username")), 0, 1, 0, 1, xoptions=0, yoptions=0, xpadding=1, ypadding=1)
        tData.attach(self.__tbUserName__, 1, 2, 0, 1, xoptions=gtk.EXPAND | gtk.FILL, yoptions=0, xpadding=1, ypadding=1)
        
        tData.attach(gtk.Label(self.__trans__("Password")), 0, 1, 1, 2, xoptions=0, yoptions=0, xpadding=1, ypadding=1)
        tData.attach(self.__tbPwd__, 1, 2, 1, 2, xoptions=gtk.EXPAND | gtk.FILL, yoptions=0, xpadding=1, ypadding=1)
        
        vBox = gtk.VBox()
        vBox.pack_start(tData, True, True)
        
        self.get_child().pack_start(vBox, True, True)
        vBox.show_all()
    
    def __closeEvent__(self, w, res):
        """
        @summary: Handle response about plugins dialog.
        @param w: GtkDialog associated.
        @param res: Response associated with the event.  
        """
        if (res == gtk.RESPONSE_OK):
            if (self.__callback__ != None):
                self.__callback__(self.__tbUserName__.get_text(), self.__tbPwd__.get_text())
           
        w.hide()

    def getUsername(self):
        """
        @summary: Gets username of google authentication
        @return: Str that contains the username
        """
        return self.__tbUserName__.get_text();
    
    def getPassword(self):
        """
        @summary: Gets password of google authentication
        @return: Str that contains the password
        """
        return self.__tbPwd__.get_text();

    def setCallback(self, callback):
        """
        @summary: Set callback to execute when confirm configuracion.
        @param callback: Function reference. 
        @note: callback model: callback (dialog: gtk.Dialog)        
        """
        self.__callback__ = callback

    def run(self):
        """
        @summary: Show option  dialog.
        """
        return super(LoginDialog, self).run()