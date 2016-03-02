#!/usr/bin/python

import logging
import os, sys
import re
from traceback import format_tb
from string import Template


SHELL_COLORS = {
    "color_fg_black": "\033[30m",
    "color_fg_red": "\033[31m",
    "color_fg_green": "\033[32m",
    "color_fg_yellow": "\033[33m",
    "color_fg_blue": "\033[34m",
    "color_fg_magenta": "\033[35m",
    "color_fg_cyan": "\033[36m",
    "color_fg_white": "\033[37m",
    "color_reset": "\033[0m",
}

LOG_LEVEL_COLORS = {
    "CRITICAL": "\033[31m",
    "ERROR": "\033[31m",
    "WARNING": "\033[33m",
    "INFO": "\033[32m",
    "DEBUG": "\033[0m",
    "NOTSET": "\033[34m",
}

 
class ColoredFormatter(logging.Formatter):
    datefmt = "%Y-%m-%d %H:%M:%S"
    _fmt = None
    _exceptionfmt = None
    useColors = True
    def __init__(self, fmt=None, datefmt="%Y-%m-%d %H:%M:%S", exceptionfmt="Traceback (most recent call last):\n%(traceback)s\n%(classname)s: %(message)s"):
        # set standard Formatter values
        self.datefmt = datefmt
        self._fmt = fmt
        self._exceptionfmt = exceptionfmt
        # set colors
        self._fmt = Template(fmt).safe_substitute(SHELL_COLORS)
        self._exceptionfmt = Template(exceptionfmt).safe_substitute(SHELL_COLORS)
        # do we have a tty?
        if sys.stdout.isatty() or os.isatty(sys.stdout.fileno()):
            self.useColors = True
        else:
            self.useColors = False
        # remove all colors
        if not self.useColors:
            self._fmt = re.sub("\033\[(\d+|;)+m", "", self._fmt)
            self._exceptionfmt = re.sub("\033\[(\d+|;)+m", "", self._exceptionfmt)

    def formatException(self, exc_info):
        return self._exceptionfmt % { 
            "classname": exc_info[0].__module__ + "." + exc_info[0].__name__,
            "message": exc_info[1],
            "traceback": "".join(format_tb(exc_info[2])).rstrip()
        }

    def format(self, record):
        fmt = self._fmt
        try:
            if self.useColors:
                self._fmt = Template(fmt).safe_substitute({ "color_level":  LOG_LEVEL_COLORS[record.levelname.upper()] })
            else:
                self._fmt = Template(fmt).safe_substitute({ "color_level":  "" })
            return super(ColoredFormatter, self).format(record)
        finally:
            self._fmt = fmt


