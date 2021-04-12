# PrivTool - Library and editor for 'Wing Commander: Privateer' save files
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
    Project metadata

The single source of truth for version number and related information.
Must be truly self-contained: do not import modules or read external files
Preferably only trivial string manipulations and basic list/tuple/dict operations
"""

# Main
# Literals only

__title__        = "privtool"
__project__      = "Privateer Tools"
__description__  = "Library and editor for 'Wing Commander: Privateer' save files"
__url__          = "https://github.com/MestreLion/privtool"

__author__       = "Rodrigo Silva (MestreLion)"
__email__        = "linux@rodrigosilva.com"

__version__      = "0.0.1"

__license__      = "GPLv3+"
__copyright__    = "Copyright (C) 2021 Rodrigo Silva (MestreLion)"


# ./cli.py

epilog = f"""{__copyright__}
License: GPLv3 or later, at your choice. See <http://www.gnu.org/licenses/gpl>
"""


# Possibly irrelevant
__status__ = "Prototype"


# Derived data
__version_info__ = tuple(map(int, __version__.split('-')[0].split('+')[0].split('.')[:3]))
if len(__version_info__) < 3: __version_info__ = (__version_info__ + 3*(0,))[:3]
