#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
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

'''

import sys
import logging

if hasattr(sys, "frozen"):
    logging._srcfile = os.path.join("logging", "__init__.pyo")

import pycamimg
try:
    __log__ = logging.getLogger(pycamimg.LogName)
except:
    __log__ = logging.getLogger()

from pycamimg.core.db import Util
from pycamimg.core.db import Constants
from pycamimg.util.Singleton import Singleton

class ConfigurationDB:
    '''
    @summary: Handle configuration of photo album from database.
    @note: It's a singleton. 
    '''
    __metaclass__ = Singleton
    
    __photoFolder__ = None
    '''
    @summary: Store folder where photos are
    '''

    def __init__(self):
        '''
        @summary: Initialize class and load parameters from db.
        '''
        self.__load__()
    
    def __load__(self):
        '''
        @summary: Load parameters from database. 
        '''
        conn = Util.getConnection()
        if (conn != None):
            pass
            curr = conn.cursor()
            curr.execute('select key, value from %s' % Constants.TBL_PARAMS)
            
            pair = curr.fetchone()
            while (pair != None):
                __log__.debug('Read parameter %s with value %s' % (pair[0], pair[1]))
                if (pair[0] == Constants.CONFIG_PARAM_PHOTO_DIR):
                    self.__photoFolder__ = pair[1]                
                pair = curr.fetchone()
                
            conn.commit()
            curr.close()
            conn.close()
        else:
            __log__.error('It can not get connection with database.')
        
    def save(self):
        '''
        @summary: Saves current configuration.
        '''
        conn = Util.getConnection()
        if (conn != None):
            queryString = 'insert or ignore into %s (key, value) values (?, ?)' % Constants.TBL_PARAMS
            updateQueryString = 'update %s set value = ? where key = ?' % Constants.TBL_PARAMS
            curr = conn.cursor()
            try:
                curr.execute(updateQueryString, (self.__photoFolder__, Constants.CONFIG_PARAM_PHOTO_DIR,))
                if (curr.rowcount == 0):
                    curr.execute(queryString, (Constants.CONFIG_PARAM_PHOTO_DIR, self.__photoFolder__,))                
                conn.commit()
            except Error, e:
                __log__.error('An error was occurred when it was saving configuration into database. %s', e)
                conn.rollback()
            curr.close()
        else:
            __log__.error('It can not get connection with database.')
        
    def getPhotoFolder(self):
        '''
        @summary: Gets folder where photo album is.
        '''
        return self.__photoFolder__
    
    def setPhotoFolder(self, folder):
        '''
        @sumary: Sets folder where photo album is.
        @param folder: Path of photo album.
        '''
        self.__photoFolder__ = folder
