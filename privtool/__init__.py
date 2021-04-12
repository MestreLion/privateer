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
    Privateer Save Game Library / Editor

Inspired by and made possible thanks to PREDIT from Wayne Sikes
"""

# Public API
__all__ = [
    'NUL', 'binopen',
    'cli',
    'Save',
]
from .binread import NUL, binopen
from .cli     import main as cli
from .model   import Save


# Project metadata
# noinspection PyUnresolvedReferences
from .__about__ import (
    __title__,
    __project__,
    __description__,
    __url__,
    __version__,
    __version_info__,
    __author__,
    __email__,
    __copyright__,
)


# https://docs.python.org/3/howto/logging.html#configuring-logging-for-a-library
import logging  # noqa: E402
logging.getLogger(__name__).addHandler(logging.NullHandler())
del logging
