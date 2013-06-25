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

class FdlTelegram(object):
	# Start delimiter
	PB_SD1		= 0x10
	PB_SD2		= 0x68
	PB_SD3		= 0xA2
	PB_SD4		= 0xDC
	PB_SC		= 0xE5

	# End delimiter
	PB_ED		= 0x16

	def __init__(self, sd, haveLE=False, da=None, sa=None,
		     fc=None, du=None, haveFCS=False, ed=None):
		self.sd = sd
		self.haveLE = haveLE
		self.da = da
		self.sa = sa
		self.fc = fc
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
			data.extend([self.sd, len(self.du), len(self.du)])
		data.append(self.sd)
		if self.da is not None:
			data.append(self.da)
		if self.sa is not None:
			data.append(self.sa)
		if self.fc is not None:
			data.append(self.fc)
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
			if sd == FdlTelegram.PB_SD1:
				# No DU
				if len(data) != 6:
					raise FdlError("Invalid FDL packet length")
				if data[5] != FdlTelegram.PB_ED:
					raise FdlError("Invalid end delimiter")
				if data[4] != FdlTelegram.calcFCS(data[1:4]):
					raise FdlError("Checksum mismatch")
				return FdlTelegram_stat0(
					da=data[1], sa=data[2], fc=data[3])
			elif sd == FdlTelegram.PB_SD2:
				# Variable DU
				le = data[1]
				if data[2] != le:
					raise FdlError("Repeated length field mismatch")
				if le < 3 or le > 249:
					raise FdlError("Invalid LE field")
				if data[3] != sd:
					raise FdlError("Repeated SD mismatch")
				if data[8+le] != FdlTelegram.PB_ED:
					raise FdlError("Invalid end delimiter")
				if data[7+le] != FdlTelegram.calcFCS(data[4:4+le+1]):
					raise FdlError("Checksum mismatch")
				du = data[7:7+(le-3)]
				if len(du) != le - 3:
					raise FdlError("FDL packet shorter than FE")
				return FdlTelegram_var(
					da=data[4], sa=data[5], fc=data[6], du=du)
			elif sd == FdlTelegram.PB_SD3:
				# Static 8 byte DU
				if len(data) != 14:
					raise FdlError("Invalid FDL packet length")
				if data[13] != FdlTelegram.PB_ED:
					raise FdlError("Invalid end delimiter")
				if data[12] != FdlTelegram.calcFCS(data[1:12]):
					raise FdlError("Checksum mismatch")
				return FdlTelegram_stat8(
					da=data[1], sa=data[2], fc=data[3], du=data[4:12])
			elif sd == FdlTelegram.PB_SD4:
				# Token telegram
				if len(data) != 3:
					raise FdlError("Invalid FDL packet length")
				return FdlTelegram_token(
					da=data[1], sa=data[2])
			elif sd == FdlTelegram.PB_SC:
				# ACK
				if len(data) != 1:
					raise FdlError("Invalid FDL packet length")
				return FdlTelegram_ack()
			else:
				raise FdlError("Invalid start delimiter")
		except IndexError:
			raise FdlError("Invalid FDL packet format")

class FdlTelegram_var(FdlTelegram):
	def __init__(self, da, sa, fc, du):
		if len(du) > 246:
			raise FdlError("Invalid data length")
		FdlTelegram.__init__(self, sd=FdlTelegram.PB_SD2,
			haveLE=True, da=da, sa=sa, fc=fc,
			du=du, haveFCS=True, ed=FdlTelegram.PB_ED)

class FdlTelegram_stat8(FdlTelegram):
	def __init__(self, da, sa, fc, du):
		if len(du) != 8:
			raise FdlError("Invalid data length")
		FdlTelegram.__init__(self, sd=FdlTelegram.PB_SD3,
			da=da, sa=sa, fc=fc,
			du=du, haveFCS=True, ed=FdlTelegram.PB_ED)

class FdlTelegram_stat0(FdlTelegram):
	def __init__(self, da, sa, fc):
		FdlTelegram.__init__(self, sd=FdlTelegram.PB_SD1,
			da=da, sa=sa, fc=fc,
			haveFCS=True, ed=FdlTelegram.PB_ED)

class FdlTelegram_token(FdlTelegram):
	def __init__(self, da, sa):
		FdlTelegram.__init__(self, sd=FdlTelegram.PB_SD4,
			da=da, sa=sa)

class FdlTelegram_ack(FdlTelegram):
	def __init__(self):
		FdlTelegram.__init__(self, sd=FdlTelegram.PB_SC)
