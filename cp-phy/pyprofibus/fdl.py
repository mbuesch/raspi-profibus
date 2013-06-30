#
# PROFIBUS - Layer 2 - Fieldbus Data Link (FDL)
#
# Copyright (c) 2013 Michael Buesch <m@bues.ch>
#
# Licensed under the terms of the GNU General Public License version 2,
# or (at your option) any later version.
#


class FdlError(Exception):
	pass

class FdlTransceiver(object):
	def __init__(self, phy):
		self.phy = phy
		self.resetFCB()

	def resetFCB(self):
		self.__fcb = 1
		self.__fcv = 0
		self.__fcbWaitingReply = False

	def __FCBnext(self):
		self.__fcb ^= 1
		self.__fcv = 1
		self.__fcbWaitingReply = False

	def poll(self, timeout=0):
		reply = self.phy.poll(timeout)
		if reply is not None:
			#TODO interpret packet
			if self.__fcbWaitingReply:
				if 1:#TODO positive SRD reply
					self.__FCBnext()
		return reply

	# Send an FdlTelegram.
	def send(self, telegram, useFCB=False):
		srd = False
		if telegram.fc & FdlTelegram.FC_REQ:
			func = telegram.fc & FdlTelegram.FC_REQFUNC_MASK
			srd = func in (FdlTelegram.FC_SRD_LO,
				       FdlTelegram.FC_SRD_HI,
				       FdlTelegram.FC_SDA_LO,
				       FdlTelegram.FC_SDA_HI,
				       FdlTelegram.FC_DDB,
				       FdlTelegram.FC_FDL_STAT,
				       FdlTelegram.FC_IDENT,
				       FdlTelegram.FC_LSAP)
			telegram.fc &= ~(FdlTelegram.FC_FCB | FdlTelegram.FC_FCV)
			if useFCB:
				if self.__fcb:
					telegram.fc |= FdlTelegram.FC_FCB
				if self.__fcv:
					telegram.fc |= FdlTelegram.FC_FCV
				if srd:
					self.__fcbWaitingReply = True
				else:
					self.__FCBnext()
		if srd:
			self.phy.profibusSend_SRD(telegram.getRawData())
		else:
			self.phy.profibusSend_SDN(telegram.getRawData())

class FdlTelegram(object):
	# Start delimiter
	SD1		= 0x10	# No DU
	SD2		= 0x68	# Variable DU
	SD3		= 0xA2	# 8 octet fixed DU
	SD4		= 0xDC	# Token telegram
	SC		= 0xE5	# Short ACK

	# End delimiter
	ED		= 0x16

	# Addresses
	ADDRESS_MASK	= 0x7F	# Address value mask
	ADDRESS_EXT	= 0x80	# DAE/SAE present

	# DAE/SAE (Address extension)
	AE_EXT		= 0x80	# Further extensions present
	AE_SEGMENT	= 0x40	# Segment address
	AE_ADDRESS	= 0x3F	# Address extension number

	# Frame Control
	FC_REQ		= 0x40	# Request

	# Request Frame Control function codes (FC_REQ set)
	FC_REQFUNC_MASK	= 0x0F
	FC_TIME_EV	= 0x00	# Time event
	FC_SDA_LO	= 0x03	# SDA low prio
	FC_SDN_LO	= 0x04	# SDN low prio
	FC_SDA_HI	= 0x05	# SDA high prio
	FC_SDN_HI	= 0x06	# SDN high prio
	FC_DDB		= 0x07	# Req. diagnosis data
	FC_FDL_STAT	= 0x09	# Req. FDL status
	FC_TE		= 0x0A	# Actual time event
	FC_CE		= 0x0B	# Actual counter event
	FC_SRD_LO	= 0x0C	# SRD low prio
	FC_SRD_HI	= 0x0D	# SRD high prio
	FC_IDENT	= 0x0E	# Req. ident
	FC_LSAP		= 0x0F	# Req. LSAP status

	# Frame Control Frame Count Bit (FC_REQ set)
	FC_FCV		= 0x10	# Frame Count Bit valid
	FC_FCB		= 0x20	# Frame Count Bit

	# Response Frame Control function codes (FC_REQ clear)
	FC_RESFUNC_MASK	= 0x0F
	FC_OK		= 0x00	# Positive ACK
	FC_UE		= 0x01	# User error
	FC_RR		= 0x02	# Resource error
	FC_RS		= 0x03	# No service activated
	FC_DL		= 0x08	# Res. data low
	FC_NR		= 0x09	# ACK negative
	FC_DH		= 0x0A	# Res. data high
	FC_RDL		= 0x0C	# Res. data low, resource error
	FC_RDH		= 0x0D	# Res. data high, resource error

	# Response Frame Control Station Type (FC_REQ clear)
	FC_STYPE_MASK	= 0x30
	FC_SLAVE	= 0x00	# Slave station
	FC_MNRDY	= 0x10	# Master, not ready to enter token ring
	FC_MRDY		= 0x20	# Master, ready to enter token ring
	FC_MTR		= 0x30	# Master, in token ring

	def __init__(self, sd, haveLE=False, da=None, sa=None,
		     fc=None, dae=(), sae=(), du=None,
		     haveFCS=False, ed=None):
		self.sd = sd
		self.haveLE = haveLE
		self.da = da
		self.sa = sa
		self.fc = fc
		self.dae = dae
		self.sae = sae
		self.du = du
		self.haveFCS = haveFCS
		self.ed = ed
		if self.haveLE:
			assert(self.du is not None)

	@staticmethod
	def calcFCS(data):
		return sum(data) & 0xFF

	def getRawData(self):
		data = []
		if self.haveLE:
			le = 3 + len(self.dae) + len(self.sae) + len(self.du)
			data.extend([self.sd, le, le])
		data.append(self.sd)
		if self.da is not None:
			data.append((self.da | FdlTelegram.ADDRESS_EXT) if self.dae
				    else self.da)
		if self.sa is not None:
			data.append((self.sa | FdlTelegram.ADDRESS_EXT) if self.sae
				    else self.sa)
		if self.fc is not None:
			data.append(self.fc)
		data.extend(self.dae)
		data.extend(self.sae)
		if self.du is not None:
			data.extend(self.du)
		if self.haveFCS:
			if self.haveLE:
				fcs = self.calcFCS(data[4:])
			else:
				fcs = self.calcFCS(data[1:])
			data.append(fcs)
		if self.ed is not None:
			data.append(self.ed)
		return data

	@staticmethod
	def fromRawData(data):
		try:
			sd = data[0]
			if sd == FdlTelegram.SD1:
				# No DU
				if len(data) != 6:
					raise FdlError("Invalid FDL packet length")
				if data[5] != FdlTelegram.ED:
					raise FdlError("Invalid end delimiter")
				if data[4] != FdlTelegram.calcFCS(data[1:4]):
					raise FdlError("Checksum mismatch")
				return FdlTelegram_stat0(
					da=data[1], sa=data[2], fc=data[3])
			elif sd == FdlTelegram.SD2:
				# Variable DU
				le = data[1]
				if data[2] != le:
					raise FdlError("Repeated length field mismatch")
				if le < 3 or le > 249:
					raise FdlError("Invalid LE field")
				if data[3] != sd:
					raise FdlError("Repeated SD mismatch")
				if data[8+le] != FdlTelegram.ED:
					raise FdlError("Invalid end delimiter")
				if data[7+le] != FdlTelegram.calcFCS(data[4:4+le+1]):
					raise FdlError("Checksum mismatch")
				du = data[7:7+(le-3)]
				if len(du) != le - 3:
					raise FdlError("FDL packet shorter than FE")
				return FdlTelegram_var(
					da=data[4], sa=data[5], fc=data[6], du=du)
			elif sd == FdlTelegram.SD3:
				# Static 8 byte DU
				if len(data) != 14:
					raise FdlError("Invalid FDL packet length")
				if data[13] != FdlTelegram.ED:
					raise FdlError("Invalid end delimiter")
				if data[12] != FdlTelegram.calcFCS(data[1:12]):
					raise FdlError("Checksum mismatch")
				return FdlTelegram_stat8(
					da=data[1], sa=data[2], fc=data[3], du=data[4:12])
			elif sd == FdlTelegram.SD4:
				# Token telegram
				if len(data) != 3:
					raise FdlError("Invalid FDL packet length")
				return FdlTelegram_token(
					da=data[1], sa=data[2])
			elif sd == FdlTelegram.SC:
				# ACK
				if len(data) != 1:
					raise FdlError("Invalid FDL packet length")
				return FdlTelegram_ack()
			else:
				raise FdlError("Invalid start delimiter")
		except IndexError:
			raise FdlError("Invalid FDL packet format")

class FdlTelegram_var(FdlTelegram):
	def __init__(self, da, sa, fc, dae, sae, du):
		if len(du) > 246:
			raise FdlError("Invalid data length")
		FdlTelegram.__init__(self, sd=FdlTelegram.SD2,
			haveLE=True, da=da, sa=sa, fc=fc,
			dae=dae, sae=sae, du=du,
			haveFCS=True, ed=FdlTelegram.ED)

class FdlTelegram_stat8(FdlTelegram):
	def __init__(self, da, sa, fc, dae, sae, du):
		if len(du) != 8:
			raise FdlError("Invalid data length")
		FdlTelegram.__init__(self, sd=FdlTelegram.SD3,
			da=da, sa=sa, fc=fc,
			dae=dae, sae=sae, du=du,
			haveFCS=True, ed=FdlTelegram.ED)

class FdlTelegram_stat0(FdlTelegram):
	def __init__(self, da, sa, fc, dae=(), sae=()):
		FdlTelegram.__init__(self, sd=FdlTelegram.SD1,
			da=da, sa=sa, fc=fc,
			dae=dae, sae=sae,
			haveFCS=True, ed=FdlTelegram.ED)

class FdlTelegram_token(FdlTelegram):
	def __init__(self, da, sa):
		FdlTelegram.__init__(self, sd=FdlTelegram.SD4,
			da=da, sa=sa)

class FdlTelegram_ack(FdlTelegram):
	def __init__(self):
		FdlTelegram.__init__(self, sd=FdlTelegram.SC)

class FdlTelegram_FdlStatReq(FdlTelegram_stat0):
	def __init__(self, da, sa):
		FdlTelegram_stat0.__init__(self, da=da, sa=sa,
			fc=FdlTelegram.FC_REQ |\
			   FdlTelegram.FC_FDL_STAT)

class FdlTelegram_IdentReq(FdlTelegram_stat0):
	def __init__(self, da, sa):
		FdlTelegram_stat0.__init__(self, da=da, sa=sa,
			fc=FdlTelegram.FC_REQ |\
			   FdlTelegram.FC_IDENT)

class FdlTelegram_LsapReq(FdlTelegram_stat0):
	def __init__(self, da, sa):
		FdlTelegram_stat0.__init__(self, da=da, sa=sa,
			fc=FdlTelegram.FC_REQ |\
			   FdlTelegram.FC_LSAP)
