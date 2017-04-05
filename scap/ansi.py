# -*- coding: utf-8 -*-
"""
    scap.ansi
    ~~~~~~~~~
    ANSI escape codes

    ..seealso:: `https://en.wikipedia.org/wiki/ANSI_escape_code`

    Copyright © 2014-2017 Wikimedia Foundation and Contributors.

    This file is part of Scap.

    Scap is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, version 3.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

FG_BLACK = 30
FG_RED = 31
FG_GREEN = 32
FG_YELLOW = 33
FG_BLUE = 34
FG_MAGENTA = 35
FG_CYAN = 36
FG_WHITE = 37
FG_RESET = 39

BG_BLACK = 40
BG_RED = 41
BG_GREEN = 42
BG_YELLOW = 43
BG_BLUE = 44
BG_MAGENTA = 45
BG_CYAN = 46
BG_WHITE = 47
BG_RESET = 49

BRIGHT = 1
DIM = 2
UNDERLINE = 4
BLINK = 5
INVERSE = 7
RESET = 22
NOBLINK = 25
RESET_ALL = 0


def esc(*args):
    """
    Get an ANSI escape code.

    >>> esc(BG_WHITE, FG_RED, BLINK) == r'\x1b[5;31;47m'
    True

    :param args: ANSI attributes
    :returns: str
    """
    return '\x1b[%sm' % ';'.join(str(arg) for arg in sorted(args))


def format(*args):
    """
    create an ansi color string from a list of color codes and plain strings.

    >>> format((FG_BLUE,BG_WHITE),'blue on white') \
            == '\x1b[34;47mblue on white\x1b[0m'
    True

    :param args: ANSI color codes and strings of text
    :returns: str
    """
    result = ""
    for arg in args:
        argtype = type(arg)
        if argtype is int:
            result += esc(arg)
        elif argtype is tuple:
            result += esc(*arg)
        else:
            result += arg
    return result + esc(RESET_ALL)


def reset():
    """
    Get the ANSI reset code.

    >>> reset() == r'\x1b[0m'
    True

    :returns: str
    """
    return esc(RESET_ALL)
