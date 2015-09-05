#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Copyright 2015 Hugo Párraga Martín

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
import os.path
import logging

if hasattr(sys, "frozen"):
    logging._srcfile = os.path.join("logging", "__init__.pyo")
import pycamimg
try:
    __log__ = logging.getLogger(pycamimg.LogName)
except:
    __log__ = logging.getLogger()

__canRun__ = True
try:
    import json
    import webbrowser
    
    import httplib2
    
    from apiclient import discovery
    from oauth2client import client
except ImportError, ie:
    __log__.error("It can not import dependency modules. %s" % ie)
    __canRun__ = False

try:
    import gtk
except Exception, e:
    __log__.fatal("It can not import pygtk module. Sure you have installed pygtk?")
    raise e

class Session(object):
    '''
    Manage a session of Google.
    '''
    def __init__(self):
        '''
        Constructor
        '''
        self.__gdataobj__ = False
        self.__httpAuth__ = None
        self.__authCode__ = None
        
        self.load()
        
    def __initializeGoogleSession__(self, checkLogin=False):
        """
        @summary: Initialize a google session.
        """
        if ((__canRun__) and (not self.__gdataobj__)):
            self.__flow__ = client.flow_from_clientsecrets(
                                                drivecore.FILE,
                                                  scope='https://www.googleapis.com/auth/drive.metadata.readonly',
                                                  redirect_uri='urn:ietf:wg:oauth:2.0:oob')
            authUri = self.__flow__.step1_get_authorize_url()
            webbrowser.open(authUri)
            self.__authCode__ = raw_input('Enter the auth code: ')
            
            credentials = self.__flow__.step2_exchange(self.__authCode__)
            self.__httpAuth__ = credentials.authorize(httplib2.Http())
            
            self.__driveService__ = discovery.build('drive', 'v2', self.__httpAuth__)
            __log__.debug("Created gdata object.")
            self.__gdataobj__ = True
            
            # Check login because it's possible session is still online
            if (checkLogin):
                self.checkLogin()
        elif (not __canRun__):
            __log__.error("It can not import gdata module. Check if gdata library for python is installed")
    
    def checkLogin(self, store=True):
        """
        @summary: Checks if there is a session.
        @return: True if there is a user on session. Otherwise False. 
        """
        ret = False
        
        try:
            if (self.__httpAuth__ != None):
                self.__token__ = self.__gdata__.GetClientLoginToken()
                
            elif ((self.__gdata__ != None) and (self.__username__ != None) and (self.__password__ != None)):
                self.__gdata__.email = self.__username__
                self.__gdata__.password = self.__password__
                self.__gdata__.source = drivecore.SOURCE
                self.__gdata__.ProgrammaticLogin()
                
                self.__token__ = self.__gdata__.GetClientLoginToken()
            else:
                __log__.info("GData is not ready to check login")
            
            if (self.isLogged()):
                ret = True
                if (store):
                    self.save()
                
        except Exception, e:
            __log__.warning("An error was ocurred when it was checking session. %s" % e)
            self.remove()
            ret = False
            
        return ret
    
    def getUsername(self):
        """
        @summary: Gets name of gdata user.
        @return: Str within username.
        """
        return self.__username__
    
    def getGdataAccess(self):
        """
        @summary: Gets google data object to access picasa.
        @return: gdata.photos.service object or None if gdata session is not initialize.
        """
        return self.__gdata__
      
    def isLogged(self):
        """
        @summary: Check if there is a session.
        @return: True when it just exists a session.
        """
        ret = False
        if ((self.__httpAuth__ != None) and (self.__authCode__ != None)):
            try:
                ret = discovery.build('drive', 'v2', self.__httpAuth__) != None
            except Exception, e:
                __log__.error("An error occurred when it was checking google login", e)
        return ret
    
    def load(self):
        """
        @summary: Load session from stored file.
        """
        self.__initializeGoogleSession__()
        filename = os.path.join(__PYCAMIMG_FOLDER__, drivecore.FILENAME)
        if (os.path.exists(filename)):
            __log__.debug("Loading gdata session on %s" % filename)
            f = open(filename, 'r')
            
            self.__username__ = f.readline()
            self.__username__ = self.__username__[:len(self.__username__) - 1]
            
            self.__token__ = f.readline()
            self.__token__ = self.__token__[:len(self.__token__) - 1]
            
            
            self.__gdata__.source = drivecore.SOURCE
            
            if (self.__username__ != None):
                self.__gdata__.email = self.__username__
            
            if (self.__token__ != None):
                self.__gdata__.SetClientLoginToken(self.__token__)
            
            
            f.close()
            __log__.info("Gdata session loaded from %s" % filename)
        else:
            __log__.debug("There is not previous session of gdata on %s" % filename)
    
    def save(self):
        """
        @summary: Save session if it's permanent. 
        """
        filename = os.path.join(__PYCAMIMG_FOLDER__, drivecore.FILENAME)
        __log__.debug("Saving google session on %s" % filename)
        f = open(filename, 'w')
        
        enc = '%s\n' % self.__authCode__
        enc += '%s\n' % self.__httpAuth__
        
        f.write(enc)
            
        f.close()
        __log__.info("Gdata session saved on %s" % filename)
        
    def remove(self):
        """
        @summary: Remove stored session
        """
        filename = os.path.join(__PYCAMIMG_FOLDER__, drivecore.FILENAME)
        __log__.debug("Removing google session. %s" % filename)
        try:
            os.remove(filename)
            __log__.info("Google session removed. %s" % filename)
            self.__authCode__ = None
            self.__httpAuth__ = None
        except OSError, e:
            __log__.error("It can not remove Google session from %s. %s" % (filename, e))
        
    
    def login(self, parent=None, forceLogin=True, store=True):
        """
        @summary: Login into google drive.
        """
        bFirst = True
        self.__initializeGoogleSession__(checkLogin=True)
        if (not self.isLogged() or forceLogin):
            # Login Google
            while (not self.isLogged() or (bFirst and forceLogin)):
                bFirst = False
                dial = LoginDialog(parent=parent)
                if (dial.run() == gtk.RESPONSE_OK):
                    self.__username__ = dial.getUsername()
                    self.__password__ = dial.getPassword()
                
                    self.checkLogin(store=store)
                    dial.destroy()
                else:
                    dial.destroy()
                    break
                
        else:
            __log__.info("Just login")
