# PrivTool - Library and editor for 'Wing Commander: Privateer' saved games
#
#    Copyright (C) 2021 Rodrigo Silva (MestreLion) <linux@rodrigosilva.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program. See <http://www.gnu.org/licenses/gpl.html>

"""
    Package setup

Mostly setup for usage as a library, such as exporting main names from modules
and adding NullHandler to package logger
"""

# Project metadata
__title__        = "privtool"
__project__      = "Privateer Tools"
__description__  = "Library and editor for 'Wing Commander: Privateer' saved games"
__url__          = "https://github.com/MestreLion/privtool"

__author__       = "Rodrigo Silva (MestreLion)"
__email__        = "linux@rodrigosilva.com"

__version__      = "0.0.1"

__license__      = "GPLv3+"
__copyright__    = "Copyright (C) 2021 Rodrigo Silva (MestreLion)"

__version_info__ = tuple(map(int, __version__.split('-')[0].split('+')[0].split('.')[:3]))
if len(__version_info__) < 3: __version_info__ = (__version_info__ + 3*(0,))[:3]


# Public API
__all__ = [
    'Save', 'cli'
]
from .main import Save, main as cli  # noqa: E402
del main

# https://docs.python.org/3/howto/logging.html#configuring-logging-for-a-library
import logging  # noqa: E402
logging.getLogger(__name__).addHandler(logging.NullHandler())
del logging
