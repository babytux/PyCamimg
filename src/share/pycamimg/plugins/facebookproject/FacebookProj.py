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
import logging
if hasattr(sys, "frozen"):
    logging._srcfile = os.path.join("logging", "__init__.pyo")
import pycamimg
try:
    __log__ = logging.getLogger(pycamimg.LogName)
except:
    __log__ = logging.getLogger()

try:
    import pygtk
    if (not (sys.platform == "win32")):
        pygtk.require('2.0')
    import gtk, gobject, gtk.gdk
except Exception, e:
    __log__.fatal("It can not import pygtk module. Sure you have installed pygtk?" )
    raise e

from pycamimg.core.plugins import IProjectType
from pycamimg.ui import FactoryControls

import gettext

__canRun__ = True
try:
    import plugins
    import facebookproject
    import facebookproject.camimgplugin
    from facebookproject.AlbumSelection import AlbumSelection
    from fbcore.SessionFB import SessionFB
except ImportError, ie:
    __log__.error("It can not import dependency modules. %s" % ie)
    __canRun__ = False

class CamimgPlugin(IProjectType.Project):
    """
    @summary: Defines facebook project structure.
    """
    
    def __init__(self):
        """
        Initialize plugin.
        """
        self.__waitAction__ = None
        self.__targetAlbum__ = None
        self.__blockWindow__ = None
    
        # Menu action
        self.__gtkAction__ = gtk.Action("FacebookProjectAction", self.__trans__("Facebook Project"), self.__trans__("Create new facebook project"), None)
        self.__gtkAction__.set_menu_item_type(gtk.ImageMenuItem)
        
        # Execution window actions
        self.__gtkActionLogin__ = gtk.Action("LoginAction", self.__trans__("Sign Up"), self.__trans__("Sign Up on facebook"), gtk.STOCK_CONNECT)
        self.__gtkActionLogin__.set_menu_item_type(gtk.ImageMenuItem)
        self.__gtkActionLogin__.set_tool_item_type(gtk.ToolButton)
        self.__gtkActionLogin__.connect("activate", self.__loginEvent__)
        
        self.__gtkActionAlbum__ = gtk.Action("SelectTargetAction", self.__trans__("Target Album"), self.__trans__("Select a target album"), gtk.STOCK_DIRECTORY)
        self.__gtkActionAlbum__.set_menu_item_type(gtk.ImageMenuItem)
        self.__gtkActionAlbum__.set_tool_item_type(gtk.ToolButton)
        self.__gtkActionAlbum__.connect("activate", self.__selectAlbumEvent__)
        
        self.__fb__ = SessionFB()
    
    def __trans__(self, msg):
        """
        @summary: Translate msg.
        @param msg: str within message. 
        @return: str translated.
        """
        return gettext.translation(facebookproject.camimgplugin.camimgpluginName, __LOCALE_FOLDER__, 
                                   languages=[__LANGKEY__], fallback = True).gettext(msg)
    
    def __loginEvent__(self, b):
        """
        @summary: Process login event.
        @param b: Action associated with event.
        """
        doLogin = True
        if (self.__fb__.isLogged()):
            doLogin = FactoryControls.getConfirmMessage(self.__trans__("You are signed up facebook\nDo you like sign up facebook?"), 
                                                          title=self.__trans__("Facebook Sign Up"), parent=self.__blockWindow__, gtkLock=gtkLock, 
                                                          returnBoolean=True)
        self.__fb__.login(self.__waitLogin__, forceLogin=doLogin)
        
        
    def __waitLogin__(self):
        """
        @summary: Function that runs when facebook login is doing.
        """
        FactoryControls.getMessage(self.__trans__("Close after sign up on facebook"), 
                                           title=self.__trans__("Facebook Sign Up"), 
                                           parent=self.__blockWindow__)
        
    def __selectAlbumEvent__(self, b):
        """
        @summary: Process select album event.
        @param b: Action associated with event. 
        """
        self.__selectAlbumOption__()
    
    def setBlockWindow(self, window):
        """
        @summary: Sets window as parent window.
        """
        self.__blockWindow__ = window
    
    def getActionWait(self):
        """
        @summary: Gets callback to wait on login facebook.
        @return: Return a callback
        @note: Callback can return a boolean value. If return is True, 
            it will save session for future uses. 
        """
        return self.__waitAction__
    
    def setActionWait(self, action):
        """
        @summary: Sets callback to wait on login facebook.
        @param action: A callback.
        @note: Callback can return a boolean value. If return is True, 
            it will save session for future uses. 
        """
        self.__waitAction__ = action
    
    def getIconName(self):
        """
        @summary: Gets name of icon that represents this project type.
        @return: String with icon filename.
        """
        return "facebook.png"
    
    def getXmlLocation(self):
        """
        @summary: Gets xml file that contains XmlMenu and its options.
        @return: String with path 
        """
        return "facebookproject.xml"
    
    def getGtkAction(self):
        """
        Gets gtk.Action of project
        """
        return self.__gtkAction__
            
    def getTypeName(self):
        """
        @summary: Gets name of this project type.
        @return: String with type project name. 
        """
        return "FacebookProject"
    
    def hasOptions(self):
        """
        @summary: Gets if the type of project has any option.
        @return: True when it has any option.
        """
        return True
    
    def getStringUIManager(self):
        """
        @summary: Gets string to add to UIManager.
        @return: str with menus.
        """
        return '<ui><toolbar name="ToolsExecute"><placeholder name="ExecuteToolItems"> \
                <toolitem name="Login" action="LoginAction" /> \
                <toolitem name="SelectTarget" action="SelectTargetAction" /> \
                </placeholder></toolbar></ui>'
    
    def getOptions(self):
        """
        @summary: Gets options of the project.
        @return: List of gtk.Actin. None if there are not options 
        """
        return [self.__gtkActionAlbum__, self.__gtkActionLogin__]
    
    def getIconsOptions(self):
        """
        @summary: Gets dictionary with icon of each action.
        @return: Dictionary of icons.
        """
        return {}
    
    def PreDoProject(self, core, blockWindow=None):
        """
        @summary: Execute before operations.
        @param core: CamCore to execute.
        @param blockWindow: GtkWindow to block by any dialog.
        @return: True if all is right.
        """
        bReturn = True
        self.__blockWindow__ = blockWindow
        
        if (self.__targetAlbum__ == None):
            bReturn = self.__selectAlbumOption__(gtkLock=False)
        
        if (self.__targetAlbum__ != None):
            albumId = None
            if (self.__targetAlbum__[1] != None):
                albumId = self.__targetAlbum__[1]
            else:
                try:
                    albumName = self.__targetAlbum__[0]
                    albumId = self.__fb__.getFacebookAccess().photos.createAlbum(albumName)["aid"]
                    __log__.info("Album %s created. Id: %s" % (albumName, albumId))
                    self.__targetAlbum__ = (albumName, albumId)
                except Exception, ex:
                    __log__.error("An error was occurred when it was creating new album %s. %s" % (self.__targetAlbum__[0], ex))
                    return False
            __log__.info("Album selected. Name: %s , Id: %s" % (self.__targetAlbum__[0], albumId))
        
        return bReturn

    def PostDoItem(self, source):
        """
        @summary: Do after operations.
        @param source: path of the source photo.
        @return: True if it is all right 
        """
        bReturn = False
        if (self.__targetAlbum__ != None):
            try:
                self.__fb__.getFacebookAccess().photos.upload(source, self.__targetAlbum__[1])
                __log__.info("Photo %s uploaded in album %s created. Id: %s" % (source, self.__targetAlbum__[0], self.__targetAlbum__[1]))
                os.remove(source)
                bReturn = True
            except IOError, ex:
                __log__.error("An error was occurred when it was uploading photo %s in album %s created. Id: %s. %s" % (source, self.__targetAlbum__[0], self.__targetAlbum__[1], ex))
        else:
            __log__.error("Target album was not selected.")
    
        return bReturn
    
    def __selectAlbumOption__(self, gtkLock=False):
        """
        @summary: Select a target album.
        @return: True when album was selected.
        """
        bReturn = False
        self.__fb__.login(self.__waitLogin__, forceLogin=False)
        if (self.__fb__.isLogged()):
            alSelection = AlbumSelection(self, parent=self.__blockWindow__)
            if (gtkLock):
                gtk.gdk.threads_enter()
            # Gets result of the selection
            try:
                # Gets result of the selection
                resAlbum = alSelection.run()
            except Exception, ex:
                __log__.error("An error has occurred.%s", ex)
                resAlbum = gtk.RESPONSE_CANCEL
            finally:
                if (gtkLock):
                    gtk.gdk.threads_leave()
            
            if (resAlbum == gtk.RESPONSE_OK):
                self.__targetAlbum__ = alSelection.getAlbum()
                bReturn = True
            
            alSelection.destroy()
        else:
            __log__.error("Facebook login failed")
        
        return bReturn
    
    def getPhotoAlbums(self):
        """
        @summary: Gets all photo albums of a user.
        @return: List with all photo albums.
        """
        albums = None
        self.__fb__.login(self.__waitLogin__, forceLogin=False)
        if (self.__fb__.isLogged()):
            __log__.debug("Getting photo albums...")
            albums = self.__fb__.getFacebookAccess().photos.getAlbums(self.__fb__.getUid())
        
        return albums