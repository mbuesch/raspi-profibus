#
# PROFIBUS DP - Layer 7
#
# Copyright (c) 2013 Michael Buesch <m@bues.ch>
#
# Licensed under the terms of the GNU General Public License version 2,
# or (at your option) any later version.
#

from pyprofibus.fdl import *
from pyprofibus.util import *


class DpError(Exception):
	pass

class DpTransceiver(object):
	def __init__(self, fdlTrans):
		self.fdlTrans = fdlTrans

	def poll(self, timeout=0):
		dpTelegram = None
		ok, fdlTelegram = self.fdlTrans.poll(timeout)
		if ok and fdlTelegram:
			if fdlTelegram.sd in (FdlTelegram.SD1,
					      FdlTelegram.SD2,
					      FdlTelegram.SD3):
				dpTelegram = DpTelegram.fromFdlTelegram(fdlTelegram)
			elif fdlTelegram.sd != FdlTelegram.SC:
				ok = False
		return (ok, dpTelegram)

	# Send a DpTelegram.
	def send(self, telegram):
		self.fdlTrans.send(telegram.toFdlTelegram(), useFCB=True)

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

	def __init__(self, da, sa, fc, dsap=None, ssap=None):
		if da < 0 or da > 127 or\
		   sa < 0 or sa > 126:
			raise DpError("Invalid DA or SA")
		self.da = da
		self.sa = sa
		self.fc = fc
		self.dsap = dsap
		self.ssap = ssap

	def __repr__(self):
		return "DpTelegram(da=%s, sa=%s, fc=%s, " \
			"dsap=%s, ssap=%s)" %\
			(intToHex(self.da), intToHex(self.sa),
			 intToHex(self.fc), intToHex(self.dsap),
			 intToHex(self.ssap))

	def toFdlTelegram(self):
		du = self.getDU()

		dae, sae = [], []
		if self.dsap is not None:
			dae.append(self.dsap)
		if self.ssap is not None:
			sae.append(self.ssap)

		le = len(du) + len(dae) + len(sae)
		if le == 0:
			return FdlTelegram_stat0(
				da=self.da, sa=self.sa, fc=self.fc)
		elif le == 8:
			return FdlTelegram_stat8(
				da=self.da, sa=self.sa, fc=self.fc,
				dae=dae, sae=sae, du=du)
		else:
			return FdlTelegram_var(
				da=self.da, sa=self.sa, fc=self.fc,
				dae=dae, sae=sae, du=du)

	@staticmethod
	def fromFdlTelegram(fdl):
		dsap = fdl.dae[0] if fdl.dae else None
		ssap = fdl.sae[0] if fdl.sae else None

		if not dsap:
			if ssap:
				raise DpError("Telegram with SSAP, but without DSAP")
			return DpTelegram_DataExchange(da=fdl.da, sa=fdl.sa,
				fc=fdl.fc, du=fdl.du[:])
		if not ssap:
			raise DpError("Telegram with DSAP, but without SSAP")

		if dsap == DpTelegram.SSAP_MS0:
			if ssap == DpTelegram.DSAP_SLAVE_DIAG:
				return DpTelegram_SlaveDiag_Con.fromFdlTelegram(fdl)
			else:
				raise DpError("Unknown SSAP: %d" % ssap)
		else:
			raise DpError("Unknown DSAP: %d" % dsap)

	# Get Data-Unit.
	# This function is overloaded in subclasses.
	def getDU(self):
		return []

class DpTelegram_DataExchange(DpTelegram):
	def __init__(self, da, sa, fc=0, du=()): #FIXME FC
		DpTelegram.__init__(self,
			da=da, sa=sa, fc=fc)
		self.du = du

	def appendData(self, data):
		if not self.du:
			self.du = [ data ]
		else:
			self.du.append(data)

	def getDU(self):
		du = DpTelegram.getDU(self)
		du.extend(self.du)
		return du

class DpTelegram_SlaveDiag_Req(DpTelegram):
	def __init__(self, da, sa,
		     fc=FdlTelegram.FC_SRD_HI |
		        FdlTelegram.FC_REQ,
		     dsap=DpTelegram.DSAP_SLAVE_DIAG,
		     ssap=DpTelegram.SSAP_MS0):
		DpTelegram.__init__(self, da=da, sa=sa, fc=fc,
				    dsap=dsap, ssap=ssap)

class DpTelegram_SlaveDiag_Con(DpTelegram):
	# Flags byte 0
	B0_STANOEX		= 0x01	# Station_Non_Existent
	B0_STANORDY		= 0x02	# Station_Not_Reay
	B0_CFGFLT		= 0x04	# Cfg_Fault
	B0_EXTDIAG		= 0x08	# Ext_Diag
	B0_NOSUPP		= 0x10	# Not_Supported
	B0_INVALSR		= 0x20	# Invalid_Slave_Response
	B0_PRMFLT		= 0x40	# Prm_Fault
	B0_MLOCK		= 0x80	# Master_Lock

	# Flags byte 1
	B1_PRMREQ		= 0x01	# Prm_Req
	B1_SDIAG		= 0x02	# Stat_Diag
	B1_ONE			= 0x04	# Always 1
	B1_WD			= 0x08	# Wd_On
	B1_FREEZE		= 0x10	# Freeze_Mode
	B1_SYNC			= 0x20	# Sync_Mode
	B1_RES			= 0x40	# Reserved
	B1_DEAC			= 0x80	# Deactivated

	# Flags byte 2
	B2_EXTDIAGOVR		= 0x80	# Ext_Diag_Overflow

	def __init__(self, da, sa, fc=FdlTelegram.FC_DL,
		     dsap=DpTelegram.SSAP_MS0,
		     ssap=DpTelegram.DSAP_SLAVE_DIAG):
		DpTelegram.__init__(self, da=da, sa=sa, fc=fc,
			dsap=dsap, ssap=ssap)
		self.b0 = 0
		self.b1 = 0
		self.b2 = 0
		self.masterAddr = 255
		self.identNumber = 0

	def __repr__(self):
		return "DpTelegram_SlaveDiag_Con(da=%s, sa=%s, fc=%s, " \
			"dsap=%s, ssap=%s) => " \
			"(b0=%s, b1=%s, b2=%s, masterAddr=%s, identNumber=%s)" %\
			(intToHex(self.da), intToHex(self.sa),
			 intToHex(self.fc),
			 intToHex(self.dsap), intToHex(self.ssap),
			 intToHex(self.b0), intToHex(self.b1), intToHex(self.b2),
			 intToHex(self.masterAddr), intToHex(self.identNumber))

	@staticmethod
	def fromFdlTelegram(fdl):
		dp = DpTelegram_SlaveDiag_Con(da=(fdl.da & FdlTelegram.ADDRESS_MASK),
					      sa=(fdl.sa & FdlTelegram.ADDRESS_MASK),
					      fc=fdl.fc,
					      dsap=fdl.dae[0], ssap=fdl.sae[0])
		try:
			dp.b0 = fdl.du[0]
			dp.b1 = fdl.du[1]
			dp.b2 = fdl.du[2]
			dp.masterAddr = fdl.du[3]
			dp.identNumber = (fdl.du[4] << 8) | fdl.du[5]
		except IndexError:
			raise DpError("Invalid Slave_Diag telegram format")
		return dp

	def getDU(self):
		return [self.b0, self.b1, self.b2,
			self.masterAddr,
			(self.identNumber >> 8) & 0xFF,
			self.identNumber & 0xFF]

class DpTelegram_SetPrm_Req(DpTelegram):
	# Station status
	STA_WD			= 0x08	# WD_On
	STA_FREEZE		= 0x10	# Freeze_Req
	STA_SYNC		= 0x20	# Sync_Req
	STA_UNLOCK		= 0x40	# Unlock_Req
	STA_LOCK		= 0x80	# Lock_Req

	def __init__(self, da, sa,
		     fc=FdlTelegram.FC_SRD_HI |
		        FdlTelegram.FC_REQ,
			dsap=DpTelegram.DSAP_SET_PRM,
			ssap=DpTelegram.SSAP_MS0):
		DpTelegram.__init__(self, da=da, sa=sa, fc=fc,
				    dsap=dsap, ssap=ssap)
		self.stationStatus = 0		# Station_Status
		self.wdFact1 = 1		# WD_Fact_1
		self.wdFact2 = 1		# WD_Fact_2
		self.minTSDR = 0		# min_Tsdr (0 = no change)
		self.identNumber = 0		# Ident_Number
		self.groupIdent = 0		# Group_Ident (Lock_Req must be set)
		self.userPrmData = []		# User_Prm_Data

	def __repr__(self):
		return "DpTelegram_SetPrm_Req(da=%s, sa=%s, fc=%s, " \
			"dsap=%s, ssap=%s) => " \
			"(stationStatus=%s, wdFact1=%s, wdFact2=%s, " \
			"minTSDR=%s, identNumber=%s, groupIdent=%s " \
			"userPrmData=%s)" %\
			(intToHex(self.da), intToHex(self.sa),
			 intToHex(self.fc),
			 intToHex(self.dsap), intToHex(self.ssap),
			 intToHex(self.stationStatus),
			 intToHex(self.wdFact1), intToHex(self.wdFact2),
			 intToHex(self.minTSDR), intToHex(self.identNumber),
			 intToHex(self.groupIdent),
			 intListToHex(self.userPrmData))

	@staticmethod
	def fromFdlTelegram(fdl):
		pass#TODO

	def getDU(self):
		du = [self.stationStatus,
		      self.wdFact1, self.wdFact2,
		      self.minTSDR,
		      (self.identNumber >> 8) & 0xFF,
		      self.identNumber & 0xFF,
		      self.groupIdent]
		du.extend(self.userPrmData)
		return du
