#
# Utility helpers
#
# Copyright (c) 2013 Michael Buesch <m@bues.ch>
#
# Licensed under the terms of the GNU General Public License version 2,
# or (at your option) any later version.
#


def intToHex(val):
	if val is None:
		return "None"
	val &= 0xFFFFFFFF
	if val <= 0xFF:
		return "0x%02X" % val
	elif val <= 0xFFFF:
		return "0x%04X" % val
	elif val <= 0xFFFFFF:
		return "0x%06X" % val
	else:
		return "0x%08X" % val

def intListToHex(valList):
	if valList is None:
		return "None"
	return "[%s]" % ", ".join(intToHex(b) for b in valList)

def boolToStr(val):
	return str(bool(val))
