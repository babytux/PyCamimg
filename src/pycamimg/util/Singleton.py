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

class Singleton(type):
    """
    @summary: Singleton implementation.
    """
    def __init__(tclass, name, bases, dct):
        tclass.__instance__ = None
        type.__init__(tclass, name, bases, dct)
 
    def __call__(tclass, *args, **kw):
        if tclass.__instance__ is None:
            tclass.__instance__ = type.__call__(tclass, *args, **kw)
        return tclass.__instance__
