#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
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

'''

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

import gettext
__canRun__ = True
try:
    import fbcore
    from .lib import facelib
except ImportError, ie:
    __log__.error("It can not import dependency modules. %s" % ie)
    __canRun__ = False

from pycamimg.ui import FactoryControls

class SessionFB(object):
    '''
    Manage a session of facebook.
    '''
    def __init__(self):
        '''
        Constructor
        '''
        self.__facebookOk__ = False
        self.__fb__ = None
        self.__session__ = None
        self.__token__ = None
        self.__loginDid__ = False
        self.__secretKey__ = None
        self.__sessionKey__ = None
        self.__uid__ = None
        self.__expire__ = -1
        self.__username__ = None
        
        self.load()
        
    def __initializeFacebookSession__(self, authToken=None, checkLogin=False):
        """
        @summary: Initialize a facebook session.
        """
        if ((__canRun__) and (not self.__facebookOk__)):
            __log__.debug("Initializating facebook api")
            __log__.debug("Creating facebook object with apikey = '%s' and secretkey = '%s'" % (fbcore.API_KEY, fbcore.SECRET_KEY))
            self.__fb__ = facelib.Facebook(fbcore.API_KEY, fbcore.SECRET_KEY, app_name=fbcore.APP_NAME, auth_token=authToken)
            self.__fb__.desktop = True
            __log__.debug("Created facebook object.")
            if (authToken == None):
                self.__token__ = self.__fb__.auth.createToken()
                __log__.debug("Created facebook token %s , with api key %s" % (self.__token__, fbcore.API_KEY))
            
            
            
            self.__facebookOk__ = True
            
            # Check login because it's possible session is still online
            if (checkLogin):
                self.checkLogin()
        elif (not __canRun__):
            __log__.error("It can not import facebook module. Check if facebook library for python is installed")
    
    def checkLogin(self, store=True):
        """
        @summary: Checks if there is a session.
        @return: True if there is a user on session. Otherwise False. 
        """
        try:
            if ((self.__fb__ != None) and (self.__token__ != None) and self.__loginDid__):
                self.__session__ = self.__fb__.auth.getSession()
                if "session_key" in self.__session__:
                    self.__sessionKey__ = str(self.__session__["session_key"])
                self.__secretKey__ = str(self.__session__["secret"])
                if "uid" in self.__session__:
                    self.__uid__ = str(self.__session__["uid"])
                if "expires" in self.__session__:
                    self.__expire__ = int(str(self.__session__["expires"]))
                    
                info = self.__fb__.users.getInfo([self.__uid__], ['name'])[0]
                if (info != None):
                    self.__username__ = str(info['name'])
                
                if ((self.__expire__ == 0) and store):
                    self.save()
            else:
                self.__session__ = None
                self.__secretKey__ = None
                self.__sessionKey__ = None
                self.__uid__ = None
                
                self.__expire__ = -1
        except facebook.FacebookError, e:
            __log__.warning("An error was ocurred when it was checking session. %s" % e)
            self.remove()
            
        return (self.__session__ != None)
    
    def getUid(self):
        """
        @summary: Gets uid of facebook user.
        @return: Str within uid.
        """
        return self.__uid__
    
    def getUsername(self):
        """
        @summary: Gets name of facebook user.
        @return: Str within username.
        """
        return self.__username__
    
    def getSessionKey(self):
        """
        @summary: Gets key of current session.
        """
        return self.__sessionKey__
    
    def getFacebookAccess(self):
        """
        @summary: Gets facebook object to access facebook.
        @return: facebook.Facebook object or None if facebook session is not initialize.
        """
        return self.__fb__
      
    def isLogged(self):
        """
        @summary: Check if there is a session.
        @return: True when it just exists a session.
        """
        return ((self.__uid__ != None) and (self.__sessionKey__ != None)) 
    
    def load(self):
        """
        @summary: Load session from stored file.
        """
        filename = os.path.join(__PYCAMIMG_FOLDER__, fbcore.FILENAME)
        if (os.path.exists(filename)):
            __log__.debug("Loading facebook session on %s" % filename)
            f = open(filename, 'r')
            
            self.__token__ = f.readline()
            self.__token__ = self.__token__[:len(self.__token__) - 1]
            
            if (self.__fb__ == None):
                self.__initializeFacebookSession__(authToken=self.__token__)
                # self.__initializeFacebookSession__()
            
            self.__secretKey__ = f.readline()
            self.__secretKey__ = self.__secretKey__[:len(self.__secretKey__) - 1]
            self.__sessionKey__ = f.readline()
            self.__sessionKey__ = self.__sessionKey__[:len(self.__sessionKey__) - 1]
            self.__uid__ = f.readline()
            self.__uid__ = self.__uid__[:len(self.__uid__) - 1]
            self.__expire__ = int(f.readline())
            self.__username__ = f.readline()
            self.__username__ = self.__username__[:len(self.__username__) - 1]
            
            
            self.__fb__.api_key = fbcore.API_KEY
            self.__fb__.secret_key = fbcore.SECRET_KEY
            self.__fb__.session_key = self.__sessionKey__
            self.__fb__.session_key_expires = self.__expire__
            self.__fb__.auth_token = self.__token__
            self.__fb__.secret = self.__secretKey__
            self.__fb__.uid = self.__uid__
            
            # self.__fb__.auth.getSession()
            
            restoreSession = {'session_key': self.__sessionKey__,
                              'secret': self.__secretKey__,
                              'uid': self.__uid__,
                              'expires': self.__expire__, }
            
            self.__session__ = restoreSession
            
            self.__loginDid__ = True
            
            self.__fb__.app_name = fbcore.APP_NAME
            
            f.close()
            __log__.info("Facebook session saved on %s" % filename)
        else:
            __log__.debug("There is not previous session of facebook on %s" % filename)
    
    def save(self):
        """
        @summary: Save session if it's permanent. 
        """
        filename = os.path.join(__PYCAMIMG_FOLDER__, fbcore.FILENAME)
        __log__.debug("Saving facebook session on %s" % filename)
        f = open(filename, 'w')
        
        enc = '%s\n' % self.__token__
        enc += '%s\n' % self.__secretKey__
        enc += '%s\n' % self.__sessionKey__
        enc += '%s\n' % self.__uid__
        enc += '%d\n' % self.__expire__
        enc += '%s\n' % self.__username__
        f.write(enc)
            
        f.close()
        __log__.info("Facebook session saved on %s" % filename)
        
    def remove(self):
        """
        @summary: Remove stored session
        """
        filename = os.path.join(__PYCAMIMG_FOLDER__, fbcore.FILENAME)
        __log__.debug("Removing facebook session. %s" % filename)
        try:
            os.remove(filename)
            __log__.info("Facebook session removed. %s" % filename)
            self.__session__ = None
            self.__secretKey__ = None
            self.__sessionKey__ = None
            self.__uid__ = None
            self.__expire__ = -1
            self.__fb__.session_key = self.__sessionKey__
            self.__fb__.session_key_expires = self.__expire__
            self.__fb__.auth_token = self.__token__
            self.__fb__.secret = self.__secretKey__
            self.__fb__.uid = self.__uid__
        except OSError, e:
            __log__.error("It can not remove Facebook session from %s. %s" % (filename, e))
        
    
    def login(self, functionWait, forceLogin=True, store=True):
        """
        @summary: Login into facebook.
        """
        bFirst = True
        self.__initializeFacebookSession__(checkLogin=True)
        if (not self.isLogged() or forceLogin):
            # Login facebook
            while (not self.isLogged() or (bFirst and forceLogin)):
                bFirst = False
                self.__loginDid__ = False
                
                self.__fb__.login(popup=True)
                __log__.info("Facebook login thrown")
                self.__loginDid__ = True
                
                functionWait()
                
                self.checkLogin(store=store)
                
            if (not self.isLogged()):
                raise Exception("Login failed")
        else:
            __log__.info("Just login")
