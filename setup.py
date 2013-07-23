#!/usr/bin/env python3

from distutils.core import setup
from pyprofibus.version import VERSION_MAJOR, VERSION_MINOR


setup(	name		= "pyprofibus",
	version		= "%d.%d" % (VERSION_MAJOR, VERSION_MINOR),
	description	= "Python PROFIBUS module",
	author		= "Michael Buesch",
	author_email	= "m@bues.ch",
	url		= "http://bues.ch/cms/hacking/profibus.html",
#	scripts		= [ "" ],
	packages	= [ "pyprofibus", ]
)
