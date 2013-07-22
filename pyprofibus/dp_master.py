#
# PROFIBUS DP - Master
#
# Copyright (c) 2013 Michael Buesch <m@bues.ch>
#
# Licensed under the terms of the GNU General Public License version 2,
# or (at your option) any later version.
#

from pyprofibus.fdl import *
from pyprofibus.dp import *
from pyprofibus.util import *


#TODO GSD parser

class DpSlaveDesc(object):
	def __init__(self, identNumber, slaveAddr, cfgDataElements):
		self.identNumber = identNumber
		self.slaveAddr = slaveAddr
		self.cfgDataElements = cfgDataElements

	def setup(self, master):
		pass#TODO

	def fillSetPrmTelegram(self, setPrm):
		setPrm.identNumber = self.identNumber
		pass#TODO

	def fillChkCfgTelegram(self, chkCfg):
		for elem in self.cfgDataElements:
			chkCfg.addCfgDataElement(elem)

class DpMaster(object):
	def __init__(self, dpmClass, phy, masterAddr):
		self.dpmClass = dpmClass
		self.phy = phy
		self.masterAddr = masterAddr

		self.slaveDescs = {}

		# Create the transceivers
		self.fdlTrans = FdlTransceiver(self.phy)
		self.dpTrans = DpTransceiver(self.fdlTrans)

	def destroy(self):
		#TODO
		if self.phy:
			self.phy.cleanup()
			self.phy = None

	def addSlave(self, slaveDesc):
		self.slaveDescs[slaveDesc.slaveAddr] = slaveDesc

	def __initializeSlave(self, slaveDesc):
		slaveDesc.setup(self)

		da, sa = slaveDesc.slaveAddr, self.masterAddr

		# Try to request the FDL status
		try:
			req = FdlTelegram_FdlStat_Req(da=da, sa=sa)
			limit = TimeLimited(5.0)
			while not limit.exceed():
				ok, reply = self.fdlTrans.sendSync(telegram=req,
								   timeout=0.1)
				if ok and reply:
					if reply.fc & FdlTelegram.FC_REQ:
						raise DpError("Slave %d replied with "
							"request bit set" % da)
					stype = reply.fc & FdlTelegram.FC_STYPE_MASK
					if stype != FdlTelegram.FC_SLAVE:
						raise DpError("Device %d is not a slave. "
							"Detected type: 0x%02X" %\
							(da, stype))
					break
				limit.sleep(0.1)
			else:
				raise DpError("Timeout in early FDL status request "
					"to slave %d" % da)
		except FdlError as e:
			raise DpError("FDL error in early FDL status request "
				"to slave %d: %s" % (da, str(e)))

		# Enable the FCB bit.
		self.fdlTrans.enableFCB(True)

		# Send a SlaveDiag request
		req = DpTelegram_SlaveDiag_Req(da=da, sa=sa)
		limit = TimeLimited(5.0)
		while not limit.exceed():
			ok, reply = self.dpTrans.sendSync(telegram=req,
							  timeout=0.1)
			if ok and reply:
				#TODO checks?
				break
		else:
			raise DpError("Timeout in early SlaveDiag request "
				"to slave %d" % da)

		# Send a SetPrm request
		req = DpTelegram_SetPrm_Req(da=da, sa=sa)
		slaveDesc.fillSetPrmTelegram(req)
		ok, reply = self.dpTrans.sendSync(telegram=req, timeout=0.3)
		if not ok:
			raise DpError("SetPrm request to slave %d failed" % da)

		# Send a ChkCfg request
		req = DpTelegram_ChkCfg_Req(da=da, sa=sa)
		slaveDesc.fillChkCfgTelegram(req)
		ok, reply = self.dpTrans.sendSync(telegram=req, timeout=0.3)
		if not ok:
			raise DpError("ChkCfg request to slave %d failed" % da)

		# Send the final SlaveDiag request
		req = DpTelegram_SlaveDiag_Req(da=da, sa=sa)
		limit = TimeLimited(1.0)
		while not limit.exceed():
			ok, reply = self.dpTrans.sendSync(telegram=req,
							  timeout=0.1)
			if ok and reply:
				#TODO additional checks?
				break
		else:
			raise DpError("Timeout in final SlaveDiag request "
				"to slave %d" % da)

	def __initializeSlaves(self):
		slaveAddrs = self.slaveDescs.keys()
		for slaveAddr in sorted(slaveAddrs):
			self.__initializeSlave(self.slaveDescs[slaveAddr])

	def initialize(self):
		# Initialize the RX filter
		self.fdlTrans.setRXFilter([self.masterAddr,
					   FdlTelegram.ADDRESS_MCAST])

		# Initialize the registered slaves
		self.__initializeSlaves()

	# Perform a data exchange with the slave at "da".
	def dataExchange(self, da, outData):
		req = DpTelegram_DataExchange_Req(da=da, sa=self.masterAddr,
						  du=outData)
		ok, reply = self.dpTrans.sendSync(telegram=req, timeout=0.1)
		if ok and reply:
			if not DpTelegram_DataExchange_Con.checkType(reply):
				raise DpError("Data_Exchange.req reply is not of "
					"Data_Exchange.con type")
			resFunc = reply.fc & FdlTelegram.FC_RESFUNC_MASK
			if resFunc == FdlTelegram.FC_DH or\
			   resFunc == FdlTelegram.FC_RDH:
				pass#TODO: Slave_Diag
			return reply.getDU()
		return None

class DPM1(DpMaster):
	def __init__(self, phy, masterAddr):
		DpMaster.__init__(self, dpmClass=1, phy=phy,
			masterAddr=masterAddr)

class DPM2(DpMaster):
	def __init__(self, phy, masterAddr):
		DpMaster.__init__(self, dpmClass=2, phy=phy,
			masterAddr=masterAddr)
