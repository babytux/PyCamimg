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

camimgpluginName = "PicasaPlugin"

class camimgplugin(ICamimgPlugin):
    """
    @summary: Define picasa plugin for pycamimg.
    """
    
    def getType(self):
        """
        @summary: Gets type of the plugin
        @return: PLUGIN_TYPE 
        """
        return PLUGIN_TYPE.PROJECT
    
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
                                   languages=[__LANGKEY__], fallback=True).gettext("Picasa Project")
    
    def getPluginModule(self):
        """
        @summary: Gets module to load plugin.
        @return: String with name of the file to load.
        """
        return "PicasaProj"
    
    def isCompiled(self):
        """
        @summary: Gets if the pluginclass is compiled.
        @return: True when is compiled.
        """
        return False
    
    def initialize(self):
        """
        @summary: Initialize plugin.
        """
        gettext.bindtextdomain(camimgpluginName, __LOCALE_FOLDER__)
        
    def getPluginDependecies(self):
        """
        @summary: Gets plugins dependencies
        """
        return ['gdatacore', ]
