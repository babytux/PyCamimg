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
import logging
if hasattr(sys, "frozen"):
    logging._srcfile = os.path.join("logging", "__init__.pyo")

import pycamimg
try:
    __log__ = logging.getLogger(pycamimg.LogName)
except:
    __log__ = logging.getLogger()

class ICamimgPlugin(object):
    
    def __init__(self):
        """
        Initialization method
        """
        return
    
    """
    @summary: It is an interface that defines the skeleton of a plugin
    """
    def log(self, level, text):
        """
        @summary: Write on log.
        @param level: Level of message.
        @param text: Message to write.  
        """
        if (level == logging.CRITICAL):
            __log__.critical(text)
        elif (level == logging.ERROR):
            __log__.error(text)
        elif(level == logging.WARNING):
            __log__.warning(text)
        elif(level == logging.INFO):
            __log__.info(text)
        else:
            __log__.debug(text)
    
    def getType(self):
        """
        @summary: Gets type of the plugin
        @return: PLUGIN_TYPE 
        """
        return PLUGIN_TYPE.UNKNOWN
        
    def getName(self):
        """
        @summary: Gets name of the plugin.
        @return: String with name of the plugin.
        """
        return ""
    
    def getId(self):
        """
        @summary: Gets ID of the plugin.
        @return: String with ID of the plugin.
        """
        return ""
    
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
    
    def initialize(self):
        """
        @summary: Initialize plugin.
        """
        return
    
    def isNeedLoad(self):
        """
        @summary:  Gets if plugin needs to pre-load.
        @return: True to load.
        """
        return True
    
    def getPluginDependecies(self):
        """
        @summary: Gets plugins dependencies
        """
        return []
    
    def hasConfiguration(self):
        """
        @summary: Gets if plugin has configuration.
        @return: True when has configuration.
        """
        return False
    
    def showPluginConfiguration(self, parent=None):
        """
        @summary: Shows plugin configuratiion dialog.
        @param parent: Parent window. 
        """
        return None
    
class PLUGIN_TYPE:
    """
    @summary: Class that will be used as enumeration.
    """
    UNKNOWN = 0
    PROJECT = 1
    OPERATION = 2
    SDK = 3