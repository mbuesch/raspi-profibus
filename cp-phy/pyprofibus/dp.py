#
# PROFIBUS DP - Layer 7
#
# Copyright (c) 2013 Michael Buesch <m@bues.ch>
#
# Licensed under the terms of the GNU General Public License version 2,
# or (at your option) any later version.
#

from pyprofibus.fdl import *


class DpError(Exception):
	pass

class DpTelegram(object):
	# Source Service Access Point number
	SSAP_MS2		= 50	# DPM2 to slave
	SSAP_MS1		= 51	# DPM1 to slave
	SSAP_MM			= 54	# Master to master
	SSAP_MS0		= 62	# Master to slave

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

	def __init__(self, da, sa, fc, dsap=None, ssap=None,
		     forceVarTelegram=False):
		if da < 0 or da > 127 or\
		   sa < 0 or sa > 126:
			raise DpError("Invalid DA or SA")
		self.da = da
		self.sa = sa
		self.fc = fc
		self.dsap = dsap
		self.ssap = ssap
		self.forceVarTelegram = forceVarTelegram

	def getFdlTelegram(self):
		du = self.getDU()

		dae, sae = [], []
		if self.dsap is not None:
			dae.append(self.dsap)
		if self.ssap is not None:
			sae.append(self.ssap)

		le = len(du) + len(dae) + len(sae)
		if le == 0 and not self.forceVarTelegram:
			return FdlTelegram_stat0(
				da=self.da, sa=self.sa, fc=self.fc,
				dae=dae, sae=sae)
		elif le == 8 and not self.forceVarTelegram:
			return FdlTelegram_stat8(
				da=self.da, sa=self.sa, fc=self.fc,
				dae=dae, sae=sae, du=du)
		else:
			return FdlTelegram_var(
				da=self.da, sa=self.sa, fc=self.fc,
				dae=dae, sae=sae, du=du)

	# Get Data-Unit.
	# This function is overloaded in subclasses.
	def getDU(self):
		return []

	# Send this telegram.
	# phy = CpPhy instance.
	# sync = True: Synchronously poll PHY response.
	def send(self, phy, sync=False):
		return self.getFdlTelegram().send(phy, sync)

class DpTelegram_DataExchange(DpTelegram):
	def __init__(self, da, sa):
		DpTelegram.__init__(self, da=da, sa=sa,
			fc=0)#TODO
		self.du = []

	def appendData(self, data):
		self.du.append(data)

	def getDU(self):
		du = DpTelegram.getDU(self)
		du.extend(self.du)
		return du

class DpTelegram_DiagReq(DpTelegram):
	def __init__(self, da, sa):
		DpTelegram.__init__(self, da=da, sa=sa,
			fc=FdlTelegram.FC_SRD_HI |
			   FdlTelegram.FC_REQ,
			dsap=DpTelegram.DSAP_SLAVE_DIAG,
			ssap=DpTelegram.SSAP_MS0)

class DpTelegram_SetPrm(DpTelegram):
	def __init__(self, da, sa):
		DpTelegram.__init__(self, da=da, sa=sa,
			fc=FdlTelegram.FC_SRD_LO |
			   FdlTelegram.FC_REQ,
			dsap=DpTelegram.DSAP_SET_PRM,
			ssap=DpTelegram.SSAP_MS0)
		pass#TODO

	def getDU(self):
		du = DpTelegram.getDU(self)
		pass#TODO
		return du
