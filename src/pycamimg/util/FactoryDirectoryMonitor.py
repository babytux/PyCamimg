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
from DirectoryMonitor import DirectoryMonitor

__monitors__ = {}
__callback__ = None

def setCallback(callback):
    """
    @summary: Set callback that receives events.
    @param callback: Callback that it will be executed when an event occur 
    """
    __callback__ = callback
    
def getMonitor(path):
    """
    @summary: If monitor exists, it will get monitor.
        Otherwise it will create a monitor and gets.
    @param path: Path to get its monitor. 
    @return: Gets DirectoryMonitor that is checking path. 
    """
    if (__monitors__.has_key(path)):
        return __monitors__[path]
    else:
        monitor = DirectoryMonitor(path)
        __monitors__[path] = monitor
        
        if (__callback__ != None):
            monitor.addListener(callback)

        return monitor
    
def removeMonitor(path):
    """
    @summary: Removes a monitor from factory.
    @param path: Path to get its monitor. 
    """
    if (__monitors__.has_key(path)):
        monitor = getMonitor(path)
        monitor.stop(checkListeners=False)
        __monitors__.pop(path)
        
def removeAll():
    """
    @summary: Removes all monitors from factory.
    """
    while (len(__monitors__) > 0):
        key = __monitors__.keys()[0]
        removeMonitor(key)
    
