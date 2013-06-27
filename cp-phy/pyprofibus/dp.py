#
# PROFIBUS DP - Layer 7
#
# Copyright (c) 2013 Michael Buesch <m@bues.ch>
#
# Licensed under the terms of the GNU General Public License version 2,
# or (at your option) any later version.
#

from fdl import *


class DpError(Exception):
	pass

class DpTelegram(object):
	# Source Service Access Point number
	SSAP_MS2		= 50
	SSAP_MS1		= 51
	SSAP_MM			= 54
	SSAP_MS0		= 62

	# Destination Service Access Point number
	DSAP_RESOURCE_MAN	= 49
	DSAP_ALARM		= 50
	DSAP_SERVER		= 51
	DSAP_EXT_USER_PRM	= 53
	DSAP_SET_SLAVE_ADR	= 55
	DSAP_RD_INP		= 56
	DSAP_RD_OUTP		= 57
	DSAP_GLOBAL_CONTROL	= 58
	DSAP_GET_CFG		= 59
	DSAP_SLAVE_DIAG		= 60
	DSAP_SET_PRM		= 61
	DSAP_CHK_CFG		= 62

	def __init__(self):
		pass#TODO

	def getFdlTelegram(self):
		pass#TODO

class DpTelegram_Prm(DpTelegram):
	def __init__(self, da, sa):
		pass#TODO
