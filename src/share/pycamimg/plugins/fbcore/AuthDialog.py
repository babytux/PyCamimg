#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Copyright 2008, 2009, 2010, 2011 Hugo Párraga Martín

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
    __log__.fatal("It can not import pygtk module. Sure you have installed pygtk?")
    raise e

from pycamimg.ui import FactoryControls
from .SessionFB import SessionFB
import fbcore.camimgplugin
import gettext

class AuthDialog (gtk.Dialog):
    """
    @summary: Class that manage facebook authentication dialog.
    """
    __DEFAULT_WINDOW_WIDTH__ = 400
    __DEFAULT_WINDOW_HEIGHT__ = 250
    
    def __init__(self, parent=None, callback=None):
        """
        @summary: Create new authentication dialog.
        @param parent: GtkWindow parent.
        """
        super(AuthDialog, self).__init__()
        
        self.__fbsession__ = SessionFB()
        
        super(AuthDialog, self).set_title(self.__trans__("Facebook Authentication"))
        super(AuthDialog, self).set_flags(gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT)
        super(AuthDialog, self).add_buttons(gtk.STOCK_OK, gtk.RESPONSE_OK)
        
        super(AuthDialog, self).set_transient_for(parent)
        if (parent != None):
            super(AuthDialog, self).set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        else:
            super(AuthDialog, self).set_position(gtk.WIN_POS_CENTER)
        
        # Add signals
        super(AuthDialog, self).connect("response", self.__closeEvent__)
        super(AuthDialog, self).set_size_request(self.__DEFAULT_WINDOW_WIDTH__, self.__DEFAULT_WINDOW_HEIGHT__)
        
        self.__initUI__()
        self.__callback__ = callback


    def __trans__(self, msg):
        """
        @summary: Translate msg.
        @param msg: str within message. 
        @return: str translated.
        """
        return gettext.translation(fbcore.camimgplugin.camimgpluginName, __LOCALE_FOLDER__,
                                   languages=[__LANGKEY__], fallback=True).gettext(msg)

    def __initUI__(self):
        """
        @summary: Initialize ui.
        """
        self.__tbUserName__ = gtk.Entry()
        self.__tbUserName__.set_editable(False)
        
        self.__tbState__ = gtk.Entry()
        self.__tbState__.set_editable(False)
        
        self.__btAuthentication__ = gtk.Button()
        self.__btAuthentication__.connect("activate", self.__loginEvent__)
        self.__btAuthentication__.connect("clicked", self.__loginEvent__)
        
        self.__btRevoke__ = gtk.Button(label=self.__trans__("Revoke"))
        self.__btRevoke__.connect("activate", self.__revokeEvent__)
        self.__btRevoke__.connect("clicked", self.__revokeEvent__)
        
        tData = gtk.Table(rows=3, columns=2)
        
        tData.attach(gtk.Label(self.__trans__("Username")), 0, 1, 0, 1, xoptions=0, yoptions=0, xpadding=1, ypadding=1)
        tData.attach(self.__tbUserName__, 1, 2, 0, 1, xoptions=gtk.EXPAND | gtk.FILL, yoptions=0, xpadding=1, ypadding=1)
        
        tData.attach(gtk.Label(self.__trans__("State")), 0, 1, 1, 2, xoptions=0, yoptions=0, xpadding=1, ypadding=1)
        tData.attach(self.__tbState__, 1, 2, 1, 2, xoptions=gtk.EXPAND | gtk.FILL, yoptions=0, xpadding=1, ypadding=1)
        
        self.__imgLogin__ = gtk.Image()
        self.__imgLogin__.set_from_file(os.path.join(__ICONS_FOLDER__, "fb-connect.png"))
        
        hbButton = gtk.HBox()
        # hbButton.pack_start(self.__imgLogin__, False, False)
        self.__btAuthentication__.set_image(self.__imgLogin__)
        hbButton.pack_start(self.__btAuthentication__, False, False)
        hbButton.pack_start(self.__btRevoke__, False, False)
        hAlign = gtk.Alignment(xalign=1, yalign=0.5)
        hAlign.add(hbButton)
        
        
        tData.attach(hAlign, 1, 2, 2, 3, xoptions=gtk.EXPAND | gtk.FILL, yoptions=gtk.FILL, xpadding=0, ypadding=0)
        
        vBox = gtk.VBox()
        vBox.pack_start(tData, True, True)
        
        self.get_child().pack_start(vBox, True, True)
        vBox.show_all()

    def __initData__(self, gtkLock=False):
        """
        @summary: Set data to dialog.
        """
        if (self.__fbsession__.getUid() != None):
            self.__tbState__.set_text(self.__trans__("Authenticated"))
            self.__tbUserName__.set_text(self.__fbsession__.getUsername())
        else:
            self.__tbState__.set_text(self.__trans__("No Authenticated"))
            self.__tbUserName__.set_text("")
    
    def __waitLogin__(self):
        """
        @summary: Function that runs when facebook login is doing.
        """
        FactoryControls.getMessage(self.__trans__("Close after sign up on facebook"),
                                   title=self.__trans__("Facebook Sign Up"),
                                   parent=self)
        self.__initData__()
    
    def __loginEvent__(self, b):
        """
        @summary: Process login event.
        @param b: Action associated with event.
        """
        doLogin = True
        if (self.__fbsession__.isLogged()):
            doLogin = FactoryControls.getConfirmMessage(self.__trans__("You are signed up facebook\nDo you like sign up facebook?"),
                                                          title=self.__trans__("Facebook Sign Up"), parent=self, gtkLock=False,
                                                          returnBoolean=True)
        self.__fbsession__.login(self.__waitLogin__, forceLogin=doLogin)
    
    def __revokeEvent__(self, b):
        """
        @summary: Process to revoke or remove previous login
        @param b: Action associated with event. 
        """
        if (FactoryControls.getConfirmMessage(self.__trans__("Do you like remove store user of facebook?"),
                                              title=self.__trans__("Facebook remove"), parent=self, gtkLock=False,
                                              returnBoolean=True)):
            self.__fbsession__.remove()
            self.__initData__()
        
    
    def __closeEvent__(self, w, res):
        """
        @summary: Handle response about plugins dialog.
        @param w: GtkDialog associated.
        @param res: Response associated with the event.  
        """
        if (res == gtk.RESPONSE_OK):
            if (self.__callback__ != None):
                self.__callback__()
           
        w.hide() 

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
        self.__initData__()
        super(AuthDialog, self).run()
