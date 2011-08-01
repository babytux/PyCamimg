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

from pycamimg.core.plugins.ICamimgPlugin import ICamimgPlugin
from pycamimg.core.plugins.ICamimgPlugin import PLUGIN_TYPE
import gettext

camimgpluginName = "gdatacore"

class camimgplugin(ICamimgPlugin):
    """
    @summary: Define google data plugin for pycamimg.
    """
    
    def getType(self):
        """
        @summary: Gets type of the plugin
        @return: PLUGIN_TYPE 
        """
        return PLUGIN_TYPE.SDK
    
    def getId(self):
        """
        @summary: Gets ID of the plugin.
        @return: String with ID of the plugin.
        """
        return camimgpluginName
        
    def getName(self):
        """
        @summary: Gets name of the plugin.
        @return: String with name of the plugin.
        """
        return gettext.translation(camimgpluginName, __LOCALE_FOLDER__, 
                                   languages=[__LANGKEY__], fallback = True).gettext("Google Data Core")
    
    def getPluginModule(self):
        """
        @summary: Gets module to load plugin.
        @return: String with name of the file to load.
        """
        return None
    
    def isCompiled(self):
        """
        @summary: Gets if the pluginclass is compiled.
        @return: True when is compiled.
        """
        return False
    
    def isNeedLoad(self):
        """
        @summary:  Gets if plugin needs to pre-load.
        @return: True to load.
        """
        return False
    
    def showPluginConfiguration(self, parent=None):
        """
        @summary: Shows plugin configuration dialog.
        @param parent: Parent window. 
        """
        from gdatacore import AuthDialog
        dialog = AuthDialog.AuthDialog(parent=parent)
        dialog.run()
        del dialog
        dialog = None
    
    def hasConfiguration(self):
        """
        @summary: Gets if plugin has configuration.
        @return: True when has configuration.
        """
        return True
    
    def initialize(self):
        """
        @summary: Initialize plugin.
        """
        gettext.bindtextdomain(camimgpluginName, __LOCALE_FOLDER__)