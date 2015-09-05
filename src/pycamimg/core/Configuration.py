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
import os, os.path
import logging, logging.handlers
if hasattr(sys, "frozen"):
    logging._srcfile = os.path.join("logging", "__init__.pyo")
import time
import ConfigParser

try:
    __log__ = logging.getLogger(pycamimg.LogName)
except:
    __log__ = logging.getLogger()

from pycamimg.util.Singleton import Singleton

class Configuration:
    __metaclass__ = Singleton
    __pathConfig__ = None
    __instanceConfig__ = None

    def __makeDefault__(self, save=True, set=True):
        """
        @summary: It creates a default configuration and save it.
        @param save: If it is true, it will save configuration into file.
        @param set: If it is true, it will set as current configuration.
        @return: Configuration made. 
        """
        config = ConfigParser.SafeConfigParser()
        
        config.add_section("NAVIGATOR")
        config.set("NAVIGATOR", "show_hiddens", ("%d" % False))
        config.add_section("TABPROJECT")
        config.set("TABPROJECT", "show_image_list", ("%d" % True))
        config.set("TABPROJECT", "max_height_list", ("%d" % 40))
        config.set("TABPROJECT", "resize_percent_list", ("%f" % 25.0))
        config.set("TABPROJECT", "max_height_imagelist", ("%d" % 200))
        config.set("TABPROJECT", "number_of_columns_iconview", ("%d" % 4))
        config.add_section("LANGUAGE")
        config.set("LANGUAGE", "default", "es")
        config.add_section("FORMATS")
        config.set("FORMATS", "formats", "JPEG")
        config.add_section("UI_CORE")
        config.set("UI_CORE", "ui_files_as_resources", ("%d" % True))
        config.set("UI_CORE", "xmlui_path", "")
        config.set("UI_CORE", "add_recursive", ("%d" % True))
        config.set("UI_CORE", "recursive_level", ("%d" % 1))
        config.set("UI_CORE", "enable_db", ("%d" % 1))
        config.add_section("LOG")
        config.set("LOG", "filename", "pycamimg.log")
        config.set("LOG", "level", ("%d" % 20))
        config.set("LOG", "format", "%(asctime)s [%(levelname)s] %(lineno)s.%(funcName)s [%(filename)s] - %(message)s")
        config.set("LOG", "sizeFileKb", ("%d" % 10240))
        config.set("LOG", "numFiles", ("%d" % 10))
        
        if (set):
            self.__setConfiguration__(config)
        if (save):
            self.saveConfiguration(config)
            
        return config
        
    def __setConfiguration__(self, configuration):
        """
        @summary: Set current configuration
        @param configuration: ConfigParser.SafeConfigParser
        """
        self.__instanceConfig__ = configuration
        
    def setSavePath(self, path):
        """
        @summary: Set path as path to save configuration.
        @param path: Path where configuration will be saved. 
        """
        self.__pathConfig__ = path
    
    def getConfiguration(self):
        """
        @summary: Gets current configuration
        """
        if (self.__instanceConfig__ == None):
            self.__makeDefault__(save=False, set=True)
        return self.__instanceConfig__
    
    def loadConfiguration(self, path=None):
        """
        @summary: Load configuration from configuration file.
        @param path: Path to configuration file.
        @return: ConfigParser.SaveConfigParser recovered. 
        """
        if ((path == None) and (self.__pathConfig__ == None)):
            __log__.error("Path is not defined")
            return None
        elif(path == None):
            __log__.debug("Set %s as config file" % self.__pathCofig__)
            path = self.__pathConfig__
        # else:
        #    __log__.debug("Set %s as new config file" % path)
        #    self.__pathConfig__ = path
        # Now is necessary set save path. 
        # otherwise Configuration can be saved 
            
        config = ConfigParser.SafeConfigParser()
        makeConfig = False
        try: 
            # Try to read the configuration file
            config.read([path])
        except:
            makeConfig = True
    
        if ((not makeConfig) and (len(config.sections()) <= 0)):
            makeConfig = True
            
        if (makeConfig):
            self.__makeDefault__()
        else:
            self.__setConfiguration__(config)
            
        return self.getConfiguration()
    
    def saveConfiguration(self, config=None):
        """
        @summary: Save configuration in config.cfg file.
        @param config: Configuration to save. If config is None, it will save getConfiguration() 
        """
        if (self.__pathConfig__ == None):
            __log__.error("__pathConfig__ was not defined")
            return
        
        f = None
        if ((config == None) and (self.__instanceConfig__ == None)):
            __log__.error("There is no a config to save")
            return
        elif(config == None):
            config = self.__instanceConfig__
            __log__.debug("I set __instanceConfig__ as config to save")
        if (not isinstance(config, ConfigParser.SafeConfigParser)):
            if (__log__ != None):
                __log__.error("There isn't configuration")
            else:
                print "There isn't configuration"
            return
    
        try:
            f = open(self.__pathConfig__, "w")
            config.write(f)
        except:
            if (__log__ != None):
                __log__.error("An error was occurred when the configuration was saving")
            else:
                print "An error was occurred when the configuration was saving"
        finally:
            # Checks the file status and closes it.
            if (f != None):
                f.close()
