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

import gobject
import gtk
import gtk.gdk
import time
import traceback
import threading
from threading import Thread
from threading import Semaphore

# gtk.gdk.threads_init()

class GIdleThreadSingle(object):
    """
    @summary: This is a pseudo-"thread" for use with the GTK+ main loop
    """

    def __init__(self, callback, *params, **kw):
        """
        @summary: Creates new GTK Thread.
        @param callback: Function to execute.
        @param params: List of parameters.  
        """
        self.__callback__ = callback
        self.__semaphore__ = Semaphore()
        self.__params__ = params
        self.__kw__ = kw
        self.__idleId__ = 0
        self.__error__ = None
        self.__result__ = None

    def __do__(self, priority=gobject.PRIORITY_LOW):
        """
        @summary: Start the generator. Default priority is low, so screen updates
            will be allowed to happen.
        @param priority: Priority of the thread. 
        """
        idle_id = gobject.idle_add(self.__generatorExecuter__,
                                   priority=priority)
        self.__semaphore__.acquire()
        self.__idleId__ = idle_id
        self.__semaphore__.release()

    def start(self, priority=gobject.PRIORITY_DEFAULT):
        """
        @summary: Start GIdleThreadSingle
        @param priority: Priority of the thread.
        @return: Id of the thread.
        """
        thread = Thread(target=self.__do__, args=(priority,))
        thread.start()
        thread.join()
        
        time.sleep(0.005)
        
        return self.__idleId__

    def wait(self, timeout=0):
        """
        @summary: Wait until the coroutine is finished or return after timeout seconds.
            This is achieved by running the GTK+ main loop.
        @param timeout: Timeout to execute the function. 
        """
        clock = time.clock
        start_time = clock()
        while self.isAlive():
            main = gobject.main_context_default()
            main.iteration(False)
            if timeout and (clock() - start_time >= timeout):
                return False
        return True

    def interrupt(self):
        """Force the generator to stop running.
        """
        if self.is_alive():
            gobject.source_remove(self.__idleId__)
            self.__semaphore__.acquire()
            self.__idleId__ = 0
            self.__semaphore__.release()

    def isAlive(self):
        """
        @summary: Returns True if the generator is still running.
        @return: True if thread is alive.
        """
        self.__semaphore__.acquire()
        alive = (self.__idleId__ != 0)
        self.__semaphore__.release()
        return alive


    error = property(lambda self: self.__error__,
                     doc="Return a possible exception that had occured "\
                         "during execution of the generator")

    def getResult(self):
        """
        @summary: Resturns the result of the operation.
        @return: The result of the function.
        """
        return self.__result__

    def __generatorExecuter__(self):
        """
        @summary: Execute callback with gtk-loop locked. 
        """
        gtk.gdk.threads_enter()
        try:
            self.__result__ = self.__callback__(*self.__params__, **self.__kw__)
        except Exception, e:
            self.__error__ = e
            traceback.print_exc()
        finally:
            gtk.gdk.threads_leave()
            
            self.__semaphore__.acquire()
            if (self.__idleId__ != 0):
                gobject.source_remove(self.__idleId__)
            self.__idleId__ = 0
            self.__semaphore__.release()
            
            return False
