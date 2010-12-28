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
import gettext, locale
import threading, thread
from threading import Thread
import time
import ConfigParser

try:
    import pygtk
    if (not (sys.platform == "win32")):
        pygtk.require('2.0')
except Exception, e:
    print >> sys.stderr, "It can not import pygtk module. Sure you have installed pygtk?"
    raise e
try:
    import gtk, gobject
    import gtk.gdk
    gobject.threads_init()
except Exception, e:
    print >> sys.stderr, "It can not import gtk module. Sure you have installed pygtk?"
    raise e

import pycamimg
from pycamimg.core.db.ConfigurationDB import ConfigurationDB
from pycamimg.core.Configuration import Configuration
from pycamimg.core.db import Util

class PyCamimg:
    
    def __init__(self):
        """
        @summary: Create new PyCamimg. 
        """
        # Gets rootpath
        sRoot = os.path.abspath(os.path.dirname(sys.argv[0]))
        preloadedCores = None
        # Scan arguments
        if (len(sys.argv) > 1):
            preloadedCores = []
            for param in range(1, len(sys.argv)):
                if (not param.startswith("-")):
                    preloadedCores.append(param)
                elif (param.startswith("--") and (param.find("=") == -1)):
                    # Parameter without whitespace. Eg. --output=python.py
                    # TODO: process parameters
                    pass
                else:
                    #Parameter with whitespace. Eg. -o python.py
                    # TODO: process parameters
                    pass
        
        self.__init__(sRoot, preloadCores=preloadedCores)

    def __init__(self, rootPath, preloadCores=None):
        """
        @summary: Create new PyCamimg.
        @param rootPath: PyCamimg folder.
        @param preloadCore: Cores that it will be loaded at the beginning.  
        """
        
        if (not isinstance(rootPath, str)):
            raise TypeError("rootPath must be str")
        if (preloadCores != None):
            if (not isinstance(preloadCores, list)):
                raise TypeError("rootPath must be a list of str")
        
        self.__log__ = None

        # Initialize variables of PyCamimg
        self.__initVariables__(rootPath)

        # Initialize local filesystem
        self.__initFilesystem__()

        # Load configuration
        Configuration().setSavePath(__CONFIG_FILE_SAVED__)
        if (os.path.exists(__CONFIG_FILE_SAVED__)):
            Configuration().loadConfiguration(__CONFIG_FILE_SAVED__)
        else:
            Configuration().loadConfiguration(__CONFIG_FILE__)

        # Initialize logging system
        self.__initLogging__()
        
        # Initialize languages
        self.__initLanguages__()

        # Enabled gtk threads
        gtk.gdk.threads_init()

        # Load plugins
        sys.path.append(os.path.join(__SHARE_PATH__, "plugins"))
        sys.path.append(os.path.join(__PERSONAL_PLUGINS__, "addons"))
        from pycamimg.core.plugins import Loader
        Loader.load(dictPaths={"plugins": __SHARE_PATH__, "addons": __PERSONAL_PLUGINS__})
        # Create a list of cores
        self.__lsCores__ = []
        if (preloadCores != None):
            from pycamimg.core.CamCore import CamCore
            for filenameCore in preloadCores:
                if (not isinstance(preloadCores, list)):
                    raise TypeError("filenameCore must be a str.")
                coreLoaded = CamCore.load(filenameCore, tempFolder=__TEMP_FOLDER__)
                if (coreLoaded != None):
                    self.__lsCores__.append(coreLoaded)
                else:
                    self.__log__.warning("It could not load core from file %s" % filenameCore)
                
                coreLoaded = None
        else:
            self.__log__.debug("There are not cores to load.")   

        self.__initDB__()

        # Init UI
        self.__initUI__()

        gtk.gdk.threads_enter()
        try:
            gtk.main()
        except Exception, ex:
            raise ex
        finally:
            gtk.gdk.threads_leave()

    def __initVariables__(self, rootPath):
        """
        @summary: Initialize variables of a files needed by PyCamimg.
        @param rootPath: Root folder of pycamimg 
        """
        if (not isinstance(rootPath, str)):
            raise TypeError("rootPath must be str")
        
        import __builtin__
        __builtin__.__EXEC_PATH__ = rootPath
        
        __builtin__.__SHARE_PATH__ = os.path.join(__EXEC_PATH__, "share", "pycamimg")
        if (not os.path.exists(__SHARE_PATH__)):
            __builtin__.__SHARE_PATH__ = os.path.join(sys.prefix, "share", "pycamimg")
        __builtin__.__LOCALE_FOLDER__ = os.path.join(__SHARE_PATH__, "locale")
        __builtin__.__ICONS_FOLDER__ = os.path.join(__SHARE_PATH__, "icons")
        __builtin__.__XMLUI_FOLDER__ = os.path.join(__SHARE_PATH__, "xml")
        __builtin__.__CONFIG_FILE__ = os.path.join(__SHARE_PATH__, "config", "config.cfg")
        __builtin__.__VERSION_FILE__ = os.path.join(__SHARE_PATH__, "config", "version.cfg")
        __builtin__.__COPYING_FILE__ = os.path.join(__SHARE_PATH__, "COPYING")
        __builtin__.__DB_SCRIPT_FILE__ = os.path.join(__SHARE_PATH__, "scripts", "db_scheme.sql")
        
        __builtin__.__PYCAMIMG_FOLDER__ = os.path.join(os.path.expanduser("~"), ".pycamimg")
        __builtin__.__LOG_FOLDER__ = os.path.join(__PYCAMIMG_FOLDER__, "log")
        __builtin__.__TEMP_FOLDER__ = os.path.join(__PYCAMIMG_FOLDER__, "temp")
        __builtin__.__CONFIG_FILE_SAVED__ = os.path.join(__PYCAMIMG_FOLDER__, "config", "config.cfg")
        __builtin__.__PERSONAL_PLUGINS__ = os.path.join(os.path.expanduser("~"), ".pycamimg", "addons")
        __builtin__.__DB_FOLDER__ = os.path.join(os.path.expanduser("~"), ".pycamimg", "db")
        
        __builtin__.__DB_FILENAME__ = "photoalbum.db"
        
        __builtin__.__STOUTPUT_FILE__ = "output.log"
        __builtin__.__STERR_FILE__ = "error.log"

    def __initFilesystem__(self):
        """
        @summary: Initialize filesystem.
        """
        if (os.path.exists(__PYCAMIMG_FOLDER__)):
            if (not os.path.isdir(__PYCAMIMG_FOLDER__)):
                os.remove(__PYCAMIMG_FOLDER__)
                os.mkdir(__PYCAMIMG_FOLDER__)
        else:
            os.mkdir(__PYCAMIMG_FOLDER__)
                
        if (not os.path.exists(__PERSONAL_PLUGINS__)):
            os.mkdir(__PERSONAL_PLUGINS__)
            
        if (not os.path.exists(__DB_FOLDER__)):
            os.mkdir(__DB_FOLDER__)
                
        if (os.path.exists(__TEMP_FOLDER__)):
            if (not os.path.isdir(__TEMP_FOLDER__)):
                os.remove(__TEMP_FOLDER__)
                os.mkdir(__TEMP_FOLDER__)
        else:
            os.mkdir(__TEMP_FOLDER__)

        if (os.path.exists(__LOG_FOLDER__)):
            if (not os.path.isdir(__LOG_FOLDER__)):
                os.remove(__LOG_FOLDER__)
                os.mkdir(__LOG_FOLDER__)
        else:
            os.mkdir(__LOG_FOLDER__)

        sys.stdout = open(os.path.join(__LOG_FOLDER__, __STOUTPUT_FILE__), "w")
        sys.stderr = open(os.path.join(__LOG_FOLDER__, __STERR_FILE__), "w")

        pathCheck, exeFile = os.path.split(__CONFIG_FILE_SAVED__)
        if (not os.path.exists(pathCheck)):
            os.mkdir(pathCheck)

    def __initLogging__(self):
        """
        @summary: Initialize logging.
        """
        filename = os.path.join(__LOG_FOLDER__, Configuration().getConfiguration().get("LOG", "filename"))

        # Set up a specific logger with our desired output level
        try:
            self.__log__ = logging.getLogger(pycamimg.LogName)
        except:
            self.__log__ = logging.getLogger()
            
        self.__log__.setLevel(Configuration().getConfiguration().getint("LOG", "level"))
        
        # create formatter
        formatter = logging.Formatter(Configuration().getConfiguration().get("LOG", "format", True))
        
        sizeLog = Configuration().getConfiguration().getint("LOG", "sizeFileKb") * 1024
        numFiles = Configuration().getConfiguration().getint("LOG", "numFiles")
        
        # Add the log message handler to the logger
        handler = logging.handlers.RotatingFileHandler(
                      filename, maxBytes=sizeLog, backupCount=numFiles)
        
        handler.setFormatter(formatter)
        
        self.__log__.addHandler(handler)
        
        self.__log__.debug("Initialize log.")

    def __initLanguages__(self):
        """
        @summary: Initialize languages.
        """
        # Gets locale directory
        self.__langsAvailable__ = {}
        self.__langs__ = {}
        
        langAvailable = os.path.join(__LOCALE_FOLDER__, "availables.cfg")
        configLangs = ConfigParser.SafeConfigParser()
        existsLangs = True
        try: 
            # Try to read the configuration file
            configLangs.read([langAvailable])
        except:
            existsLangs = False
    
        if ((not existsLangs) and (len(configLangs.sections()) <= 0)):
            existsLangs = False
            
        if (existsLangs):
            for lang in configLangs.sections():
                loc = configLangs.get(lang, "locale")
                win = configLangs.get(lang, "windows")
                strLang = configLangs.get(lang, "str")
                
                self.__langsAvailable__[lang] = (loc, win, strLang)
                self.__langs__[lang] = strLang 
        else:
            self.__log__.error("There is not available languages config file.")

        del configLangs
        
        self.__currLang__ = Configuration().getConfiguration().get("LANGUAGE", "default")
        self.__setLanguage__(self.__currLang__)

        # Set domain
        gettext.bindtextdomain(pycamimg.gettextName, __LOCALE_FOLDER__)
        gettext.textdomain(pycamimg.gettextName)

    def __setLanguage__ (self, key):
        """
        @summary: Sets a language as current language.
        @param key: Key of language that it will be selected. 
        """
        if (not isinstance(key, str)):
            raise TypeError("key must be str")
        
        self.__currLang__ = key
        
        currentKey, currentEncoding = locale.getdefaultlocale()
        
        langsTrans = []
        for keyTrans, tupleTrans in self.__langsAvailable__.iteritems():
            if (sys.platform == "win32"):
                langsTrans.append(tupleTrans[1])
            else:
                langsTrans.append(tupleTrans[0])
        
        tupleLang = None
        if (len(self.__langsAvailable__) > 0):
            if (self.__langsAvailable__.has_key(key)):
                tupleLang = self.__langsAvailable__[key]
            
        if (tupleLang != None):
            localeKey, windowsKey, strKey = tupleLang
        
            if (sys.platform == "win32"):
                localeKey = windowsKey
        else:
            localeKey = currentKey
            
        try:
            if (localeKey != ""):
                #locale.setlocale(locale.LC_ALL, (localeKey, currentEncoding))
                locale.setlocale(locale.LC_ALL, localeKey)
            else:
                locale.setlocale(locale.LC_ALL, "")
                self.__currLang__, encoding = locale.getlocale(locale.LC_ALL)
        except:
            if (self.__log__ != None):
                self.__log__.error("It can not set %s as current locale. Trying with default locale" % localeKey)
            else:
                print "It can not set %s as current locale. Trying with default locale" % key
            try:
                if (sys.platform == "win32"):
                    locale.setlocale(locale.LC_ALL, "english")
                else:
                    locale.setlocale(locale.LC_ALL, "en")
                self.__currLang__ = "en"
            except Exception, e:
                if (self.__log__ != None):
                    self.__log__.error("It can not set default locale. %s" % e)
                else:
                    print "It can not set default locale. %s" % e  
                    
        # Install translation operation
        # register the gettext function for the whole interpreter as "_"
        import __builtin__
        # Get the language to use
        __builtin__.__LANGS__ = langsTrans
        __builtin__.__LANGKEY__ = localeKey
        __builtin__._ = gettext.translation("pycamimg", __LOCALE_FOLDER__, 
                                            languages=[__LANGKEY__], fallback = True).gettext

    def __initDB__(self):
        """
        @summary: Initialize DB when db option is activated. 
        """
        if (Configuration().getConfiguration().getboolean("UI_CORE", "enable_db")):
            Util.generateDB()
            #Initialize configuration from database.
            ConfigurationDB()

    def __initUI__(self):
        """
        @summary: Initialize UI of PyCamimg.
        """
        #Initialize locks
        self.__expandTree__ = threading.Lock()
        
        from pycamimg.ui.Main import MainWindow
        
        self.__mainWindow__ = MainWindow(
            self.__lsCores__, 
            domain=pycamimg.gettextName,
            languages=self.__langs__,
            currentLang=self.__currLang__,
            setLanguage=self.__setLanguage__)
        

        self.__mainWindow__.show()    
        
if __name__ == "__main__":
    rootPath = os.path.abspath(os.path.dirname(sys.argv[0]))
    PyCamimg(rootPath)
        
