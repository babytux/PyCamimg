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
import sqlite3
import os.path
import logging

if hasattr(sys, "frozen"):
    logging._srcfile = os.path.join("logging", "__init__.pyo")

import pycamimg
try:
    __log__ = logging.getLogger(pycamimg.LogName)
except:
    __log__ = logging.getLogger()

def getConnection() :
    '''
    @summary: Gets new connection with database.
    @return: sqlite3.Connection object.
    '''
    path = os.path.join(__DB_FOLDER__, __DB_FILENAME__)
    __log__.debug('Getting sqlite connection from %s' % path)
    return sqlite3.connect(path)


def generateDB():
    '''
    @summary: Generates db schema.
    '''
    sql = None
    try:
        h = open(__DB_SCRIPT_FILE__, 'r')
        sql = u"".join(h.readlines())
    except IOError, err:
        __log__.error('An IO error was occurred when it was loading script db file [%s]. %s' (__DB_SCRIPT_FILE__, err))
    except Exception, e:
        __log__.error('An error was occurred when it was loading script db file [%s]. %s' (__DB_SCRIPT_FILE__, e))
    
    if (sql != None):
        conn = getConnection()
        if (conn != None):
            cur = conn.cursor()
            try:
                cur.executescript(sql)
                conn.commit()
            except Error, e:
                __log__.error('An error was occurred when it was generating database. %s' % e)
                conn.rollback()
            cur.close()
        conn.close
    else:
        __log__.debug('It can not get script to generate database, or %s is empty' % __DB_SCRIPT_FILE__)
        
def checkDB(generates=False):
    '''
    @summary: Checks if database exists.
    @param generates: True to generate database when it does not exist. 
    '''
    path = os.path.join(__DB_FOLDER__, __DB_FILENAME__)
    if (os.path.exists(path)):
        __log__.debug('DB file exists on %s' % path)
        generates = True
    else:
        __log__.info('DB file do not exists on %s' % path)
    
    if (generates):
        __log__.debug('It will generates db scheme on %s' % path)
        generateDB()
    
