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
import facebookproject.camimgplugin
from pycamimg.ui import UIUtils

class AlbumSelection(gtk.Dialog):
    """
    @summary: Dialog to select target album.
    """
    
    def __init__(self, facebookProject, parent=None):
        """
        Creates new album selection dialog.
        @param facebookProject: facebook project that is the caller.
        @param parent: GtkWindow that is the parent window.
        """
        gtk.Dialog.__init__(self)
        
        self.__facebook__ = facebookProject
        
        # Dialog properties.
        self.add_buttons(gtk.STOCK_OK, gtk.RESPONSE_OK, gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        self.set_default_response(gtk.RESPONSE_CANCEL)
        self.set_has_separator(True)
        self.set_title(self.__trans__("Album selection - Facebook"))
        
        self.set_modal(True)
        if (parent == None):
            self.set_position(gtk.WIN_POS_CENTER)
        else:
            self.set_transient_for(parent)
            self.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        
        # ComboBox for album selection.
        self.__cbModel__ = gtk.ListStore(gobject.TYPE_STRING,
                                         gobject.TYPE_STRING,
                                         gobject.TYPE_INT64)
        self.__refresh__(None)
        
        self.__cbAlbums__ = gtk.ComboBox(self.__cbModel__)
        cell = gtk.CellRendererText()
        self.__cbAlbums__.pack_start(cell, True)
        self.__cbAlbums__.add_attribute(cell, 'text', 0)
        self.__cbAlbums__.set_title(self.__trans__("Album selection"))
        
        # Radiobuttons
        self.__rbNewAlbum__ = gtk.RadioButton(label=self.__trans__("New Album"))
        self.__rbNewAlbum__.set_active(True)
        self.__rbNewAlbum__.connect("toggled", self.__changeMode__)
        self.__rbSelectAlbum__ = gtk.RadioButton(group=self.__rbNewAlbum__, label=self.__trans__("Select Album"))
        self.__rbSelectAlbum__.connect("toggled", self.__changeMode__)
        
        # Button to update combo of albums
        self.__bUpdateAlbums__ = gtk.Button(stock=gtk.STOCK_REFRESH)
        self.__bUpdateAlbums__.connect("activate", self.__refresh__)
        
        # Textbox to set name of a new album
        self.__eNewAlbum__ = gtk.Entry()
        
        # Pack 
        hbSelectAlbum = gtk.HBox()
        hbSelectAlbum.pack_start(self.__rbSelectAlbum__)
        hbSelectAlbum.pack_start(self.__cbAlbums__)
        hbSelectAlbum.pack_start(self.__bUpdateAlbums__)
        
        hbNewAlbum = gtk.HBox()
        hbNewAlbum.pack_start(self.__rbNewAlbum__)
        hbNewAlbum.pack_start(self.__eNewAlbum__)
        
        vbMain = gtk.VBox()
        vbMain.pack_start(hbNewAlbum, expand=False)
        vbMain.pack_start(hbSelectAlbum, expand=False)
        
        self.vbox.pack_start(vbMain, expand=True, fill=True)
        
        self.__changeMode__(self.__rbNewAlbum__)
        
        vbMain.show_all()

    def __trans__(self, msg):
        """
        @summary: Translate msg.
        @param msg: str within message. 
        @return: str translated.
        """
        return gettext.translation(facebookproject.camimgplugin.camimgpluginName, __LOCALE_FOLDER__, 
                                   languages=[__LANGKEY__], fallback = True).gettext(msg)

    def __refresh__(self, b):
        """
        @summary: Handle for refresh button event.
        @param b: Button associated with the event. 
        """    
        self.__cbModel__.clear()
        albums = self.__facebook__.getPhotoAlbums()
        if (albums != None):
            for album in albums:
                __log__.debug("Album detected: %s" % album["name"])
                UIUtils.addIterListView(self.__cbModel__, (album["name"], album["aid"], albums.index(album)), doGObject=False)
        else:
            __log__.info("No se han recuperado albums.")
            
    def __changeMode__(self, rb):
        """
        @summary: Handle for setting to enable or disable ui controls.
        @param rb: RadioButton that is associated with the event. 
        """
        if ((rb == self.__rbSelectAlbum__) and self.__rbSelectAlbum__.get_active()):
            self.__cbAlbums__.set_sensitive(True)
            self.__bUpdateAlbums__.set_sensitive(True)
            self.__eNewAlbum__.set_sensitive(False)
        elif ((rb == self.__rbNewAlbum__) and self.__rbNewAlbum__.get_active()):
            self.__cbAlbums__.set_sensitive(False)
            self.__bUpdateAlbums__.set_sensitive(False)
            self.__eNewAlbum__.set_sensitive(True)
        else:
            __log__.warning("Unknown radiobutton")
            
    def getAlbum(self):
        """
        @summary: Gets name of the selected album.
        @return: Tuple with a the name and id of selected album.
        """
        sAlbum = None
        sAlbumId = None
        if (self.__rbNewAlbum__.get_active()):
            sAlbum = self.__eNewAlbum__.get_text()
            sAlbum.strip()
            sAlbumId = None
        elif (self.__rbSelectAlbum__.get_active()):
            sAlbum = self.__cbModel__.get_value(self.__cbAlbums__.get_active_iter(), 0)
            sAlbumId = self.__cbModel__.get_value(self.__cbAlbums__.get_active_iter(), 1)
        else:
            __log__.warning("Unknown radiobutton")
            
        return (sAlbum, sAlbumId)