#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
:Name:
    utility.py

:Authors:
    Soufian Salim (soufi@nsal.im)
"""

import io
import time


def timed_print(message):
    """
    Prints a string prefixed by the current date and time
    """
    print("[{0}] {1}".format(time.strftime("%H:%M:%S"), message))


def remove_extension(filename):
	"""
	Returns a filename without the extension
	"""
	if "." in filename:
		return filename[:filename.index(".")]
	else:
		return filename


def save_to_file(string, filepath):
    """
    Saves string to file
    """
    with io.open(filepath, "w", encoding="utf-8") as f:
        f.write(unicode(string))