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

import math
import threading


#TODO GSD parser

class DpSlaveState():
	def __init__(self):
		self.__state=""	# invalid state
		self.__next=""
		self.__last=""
		self.limit = TimeLimited(0.01)	# timeout object
		self.setDataValid(False)
		self.RetryReset()
	
	def RetryReset(self):
		self.__retryCnt = 0
	def RetryFailed(self):
		self.__retryCnt += 1
	def RetryOver(self, limit):
		return (self.__retryCnt > int(limit))
	
	def setDataValid(self, valid):
		self.__dataValid =(valid == True)
	def isValid(self):
		return (self.__dataValid == True)
	
	def Set(self, txt):
		if txt in ["init","wdiag","wprm","wcfg","wdxrd","dxchg"]:
			self.__next=txt
			if txt != "dxchg":
				self.setDataValid(False)
		else:
			raise DpError("setting invalid slave state")			
	def setInit(self):
		self.Set("init")
	def setWaitDiag(self):
		self.Set("wdiag")
	def setWaitPrm(self):
		self.Set("wprm")
	def setWaitCfg(self):
		self.Set("wcfg")
	def setWaitDxReady(self):
		self.Set("wdxrd")
	def setDataEx(self):
		self.Set("dxchg")
		
	def apply(self):
		self.__last = self.__state
		self.__state = self.__next	
	def changed(self):
		return (self.__last != self.__state)	
	def changing(self):
		return (self.__next != self.__state)
			
	def Is(self, txt):
		return (txt == self.__state)		
	def isInit(self):
		return self.Is("init")
	def isWaitDiag(self):
		return self.Is("wdiag")
	def isWaitPrm(self):
		return self.Is("wprm")
	def isWaitCfg(self):
		return self.Is("wcfg")
	def isWaitDxReady(self):
		return self.Is("wdxrd")
	def isDataEx(self):
		return self.Is("dxchg")
		
	def getNext(self):
		return str(self.__next)
			
class DpSlaveDesc(object):
	def __init__(self,
		     identNumber,
		     slaveAddr,
		     inputAddressRangeSize,
		     outputAddressRangeSize):
		self.identNumber = identNumber
		self.slaveAddr = slaveAddr
		self.inputAddressRangeSize = inputAddressRangeSize
		self.outputAddressRangeSize = outputAddressRangeSize
		self.req = None	# request message
		
		# io buffer for threadsafe PLC data exchange
		self.dp_Lock = threading.Lock()	# handle bus buffers
		self.dp_di = [0]*int(inputAddressRangeSize)
		self.dp_do = [0]*int(outputAddressRangeSize)
		
		# state of para, config, dataex
		self.state = DpSlaveState()
		
		# Context for FC-Bit toggeling
		self.fcb = FdlFCB(False)	# default: disabled

		# Prepare a Set_Prm telegram.
		self.setPrmTelegram = DpTelegram_SetPrm_Req(
					da = self.slaveAddr,
					sa = None)
		self.setPrmTelegram.identNumber = self.identNumber

		# Prepare a Chk_Cfg telegram.
		self.chkCfgTelegram = DpTelegram_ChkCfg_Req(
					da = self.slaveAddr,
					sa = None)

		self.isParameterised = False

	def __repr__(self):
		return "DPSlaveDesc(identNumber=%s, slaveAddr=%d)" %\
			(intToHex(self.identNumber), self.slaveAddr)
	
	def GetDpDo(self):
		# accessed by bus scheduler
		self.dp_Lock.acquire()
		retval = []
		for i in self.dp_do:
			retval.append(i)
		self.dp_Lock.release()
		return retval
		
	def SetNewDi(self, data):
		# accessed by bus scheduler
		self.dp_Lock.acquire()
		del self.dp_di[:]	# empty list
		if not data is None:
			for i in data:
				self.dp_di.append(i)
		else:
			self.dp_di = [0]*self.inputAddressRangeSize
		self.dp_Lock.release()
		return 
	
	def SetNewDo_GetDi(self, data):
		# accessed by PLC / user application
		self.dp_Lock.acquire()
		del self.dp_do[:]	# empty list
		for i in data:
			self.dp_do.append(i)
		retval = []
		for i in self.dp_di:
			retval.append(i)
		self.dp_Lock.release()
		return retval
		
	def setSyncMode(self, enabled):
		"""Enable/disable sync-mode.
		Must be called before parameterisation."""

		assert(not self.isParameterised)
		if enabled:
			self.setPrmTelegram.stationStatus |= DpTelegram_SetPrm_Req.STA_SYNC
		else:
			self.setPrmTelegram.stationStatus &= ~DpTelegram_SetPrm_Req.STA_SYNC

	def setFreezeMode(self, enabled):
		"""Enable/disable freeze-mode.
		Must be called before parameterisation."""

		assert(not self.isParameterised)
		if enabled:
			self.setPrmTelegram.stationStatus |= DpTelegram_SetPrm_Req.STA_FREEZE
		else:
			self.setPrmTelegram.stationStatus &= ~DpTelegram_SetPrm_Req.STA_FREEZE

	def setGroupMask(self, groupMask):
		"""Assign the slave to one or more groups.
		Must be called before parameterisation."""

		assert(not self.isParameterised)
		self.setPrmTelegram.groupIdent = groupMask

	def setWatchdog(self, timeoutMS):
		"""Set the watchdog timeout (in milliseconds).
		If timeoutMS is 0, the watchdog is disabled."""

		if timeoutMS <= 0:
			# Disable watchdog
			self.setPrmTelegram.stationStatus &= ~DpTelegram_SetPrm_Req.STA_WD
			return

		# Enable watchdog
		self.setPrmTelegram.stationStatus |= DpTelegram_SetPrm_Req.STA_WD

		# Set timeout factors
		fact1 = timeoutMS / 10
		fact2 = 1
		while fact1 > 255:
			fact2 *= 2
			fact1 /= 2
			if fact2 > 255:
				raise DpError("Watchdog timeout %d is too big" % timeoutMS)
		fact1 = min(255, int(math.ceil(fact1)))
		self.setPrmTelegram.wdFact1 = fact1
		self.setPrmTelegram.wdFact2 = fact2

class DpMaster(object):
	def __init__(self, dpmClass, phy, masterAddr, debug=False):
		self.dpmClass = dpmClass
		self.phy = phy
		self.masterAddr = masterAddr
		self.debug = debug

		self.slaveDescs = {}

		# Create the transceivers
		self.fdlTrans = FdlTransceiver(self.phy)
		self.dpTrans = DpTransceiver(self.fdlTrans)

	def __debugMsg(self, msg):
		if self.debug:
			print(msg)

	def destroy(self):
		#TODO
		if self.phy:
			self.phy.cleanup()
			self.phy = None

	def addSlave(self, slaveDesc):
		"""Register a slave."""

		self.slaveDescs[slaveDesc.slaveAddr] = slaveDesc

	def getSlaveList(self):
		"""Get a list of registered DpSlaveDescs, sorted by address."""

		return [ desc for addr, desc in sorted(self.slaveDescs.items(),
						       key = lambda x: x[0]) ]

	def runAllSlaves(self):		
		slaveAddrs = self.slaveDescs.keys()
		for slaveAddr in sorted(slaveAddrs):
			self.runSlave(self.slaveDescs[slaveAddr])
	
	def runSlave(self, slave):	# scheduler
		da, sa = slave.slaveAddr, self.masterAddr
		if slave.state.isInit():
			if slave.state.changed():
				slave.isParameterised = False
				self.__debugMsg("Initializing slave %d..." % da)
				
				# Enable the FCB bit.
				slave.fcb.enableFCB(True)
				
				slave.req = FdlTelegram_SrdHi_Req(da=da, sa=sa)
			#
			ok, reply = self.fdlTrans.sendSync(	slave.fcb, telegram=slave.req, timeout=0.1)
			if ok and reply:
				stype = reply.fc & FdlTelegram.FC_STYPE_MASK
				if reply.fc & FdlTelegram.FC_REQ:
					err_str="Slave %d replied with request bit set" % da
					self.__debugMsg(err_str)
					#raise DpError(err_str)
				elif stype != FdlTelegram.FC_SLAVE:
					err_str="Device %d is not a slave. Detected type: 0x%02X" %(da, stype)
					self.__debugMsg(err_str)
					#raise DpError(err_str)
				else:
					self.__debugMsg("slave.state.setWaitDiag()" )
					slave.state.setWaitDiag()
			#
		elif slave.state.isWaitDiag():
			if slave.state.changed():
				# Enable the FCB bit.
				slave.fcb.enableFCB(True)

				# Send a SlaveDiag request
				self.__debugMsg("Requesting Slave_Diag from slave %d..." % da)
				slave.req = DpTelegram_SlaveDiag_Req(da=da, sa=sa)
			ok, reply = self.dpTrans.sendSync(\
					slave.fcb, telegram=slave.req, timeout=0.1)
			if ok and reply:
				#TODO checks?
				slave.state.setWaitPrm()
			else:
				slave.state.setInit()
			#
		elif slave.state.isWaitPrm():
			if slave.state.changed():
				self.__debugMsg("Sending Set_Prm to slave %d..." % da)
				slave.req = slave.setPrmTelegram
				slave.req.sa = sa # Assign master address
			ok, reply = self.dpTrans.sendSync(\
					slave.fcb, telegram=slave.req, timeout=0.3)
			if ok:
				slave.state.setWaitCfg()
			else:
				slave.state.setInit()
			#
		elif slave.state.isWaitCfg():
			if slave.state.changed():
				self.__debugMsg("Sending Ckh_Cfg to slave %d..." % da)
				slave.req = slave.chkCfgTelegram
				slave.req.sa = sa # Assign master address
			ok, reply = self.dpTrans.sendSync(\
					slave.fcb, telegram=slave.req, timeout=0.3)
			if ok:
				slave.state.setWaitDxReady()
			else:
				slave.state.setInit()
			#
		elif slave.state.isWaitDxReady():
			if slave.state.changed():
				self.__debugMsg("Requesting Slave_Diag from slave %d..." % da)
				slave.state.limit = TimeLimited(1.0)
				slave.req = DpTelegram_SlaveDiag_Req(da=da, sa=sa)
			ok, reply = self.dpTrans.sendSync(\
				slave.fcb, telegram=slave.req, timeout=0.1)
			if ok and reply:
				#TODO additional checks?
				if reply.HasExtDiag():
					#TODO turn on red DIAG-LED
					pass
				if reply.IsReadyDataEx():
					slave.state.setDataEx()
				elif reply.NeedsNewPrmCfg() or slave.state.limit.exceed(): 
					slave.state.setInit()
				else:
					pass
			#
		elif slave.state.isDataEx():
			if slave.state.changed():
				self.__debugMsg("Initialization finished. "
					"Running Data_Exchange @slave %d..." % da)
				slave.state.RetryReset()
				slave.isParameterised = True
			# TODO: add support for in/out- only slaves
			outData=slave.GetDpDo()# cyclic updated output bytes
			try:
				inData = self.dataExchange(da, outData)
				slave.state.setDataValid(True)
				slave.state.RetryReset()
			except:
				inData = None
				slave.state.setDataValid(False)
				slave.state.RetryFailed()
			slave.SetNewDi(inData) # thread safe hand over to PLC
			if slave.state.RetryOver(4):
				slave.state.setInit()	# communication lost
			elif slave.state.RetryOver(2):
				try:
					ready, reply = self.__DiagSlave(slave)
					if not ready and reply.NeedsNewPrmCfg():
						slave.state.setInit()
				except:
					self.__debugMsg("Diag Exception @slave %d..." % da)
			#
		else:
			slave.state.setInit()
		if slave.state.changing():
			self.__debugMsg("slave[%02X].state --> %s"%(da,slave.state.getNext()))
		slave.state.apply()

	def __DiagSlave(self, slaveDesc):
		da, sa = slaveDesc.slaveAddr, self.masterAddr

		# Send the final SlaveDiag request to check readyness for data exchange
		self.__debugMsg("Requesting Slave_Diag from slave %d..." % da)
		req = DpTelegram_SlaveDiag_Req(da=da, sa=sa)
		limit = TimeLimited(1.0)
		ready = False
		while not limit.exceed():
			ok, reply = self.dpTrans.sendSync(\
				slaveDesc.fcb, telegram=req, timeout=0.1)
			if ok and reply:
				#TODO additional checks?
				if reply.HasExtDiag():
					self.__debugMsg("Slave(%d) HasExtDiag" % da)
					pass
				if reply.IsReadyDataEx():
					ready = True
					break
				elif reply.NeedsNewPrmCfg():
					#self.__debugMsg("Slave(%d) NeedsNewPrmCfg" % da)
					pass					
		else:
			raise DpError("Timeout in final SlaveDiag request "
				"to slave %d" % da)
		time.sleep(0.05)
		return ready, reply

	def DiagSlaves(self):
		all_ready = True
		slaveAddrs = self.slaveDescs.keys()
		for slaveAddr in sorted(slaveAddrs):
			ready, reply = self.__DiagSlave(self.slaveDescs[slaveAddr])
			all_ready = all_ready and ready
		return all_ready

	def initialize(self):
		"""Initialize the DPM."""

		# Initialize the RX filter
		self.fdlTrans.setRXFilter([self.masterAddr,
					   FdlTelegram.ADDRESS_MCAST])

	def dataExchange(self, da, outData):
		"""Perform a data exchange with the slave at "da"."""
		slaveDesc = self.slaveDescs[da]
		req = DpTelegram_DataExchange_Req(da=da, sa=self.masterAddr,
						  du=outData)
		ok, reply = self.dpTrans.sendSync(\
				slaveDesc.fcb, telegram=req, timeout=0.1)
		if ok and reply:
			if not DpTelegram_DataExchange_Con.checkType(reply):
				raise DpError("Data_Exchange.req reply is not of "
					"Data_Exchange.con type")
			resFunc = reply.fc & FdlTelegram.FC_RESFUNC_MASK
			if resFunc == FdlTelegram.FC_DH or\
			   resFunc == FdlTelegram.FC_RDH:
				pass#TODO: Slave_Diag
			if resFunc == FdlTelegram.FC_RS:	# service not active on slave?
				raise DpError("Service not active on slave %d" % da)
			return reply.getDU()
		return None

	def __syncFreezeHelper(self, fcb, groupMask, controlCommand):
		globCtl = DpTelegram_GlobalControl(da=FdlTelegram.ADDRESS_MCAST,
						   sa=self.masterAddr)
		globCtl.controlCommand |= controlCommand
		globCtl.groupSelect = groupMask & 0xFF
		ok, reply = self.dpTrans.sendSync(\
			fcb, telegram=globCtl, timeout=0.1)
		if ok:
			assert(not reply) # SDN
		else:
			raise DpError("Failed to send Global_Control to "
				"group-mask 0x%02X" % groupMask)

	def syncMode(self, fcb, groupMask):
		"""Set SYNC-mode on the specified groupMask.
		If groupMask is 0, all slaves are addressed."""

		self.__syncFreezeHelper(fcb, groupMask, DpTelegram_GlobalControl.CCMD_SYNC)

	def syncModeCancel(self, fcb, groupMask):
		"""Cancel SYNC-mode on the specified groupMask.
		If groupMask is 0, all slaves are addressed."""

		self.__syncFreezeHelper(fcb, groupMask, DpTelegram_GlobalControl.CCMD_UNSYNC)

	def freezeMode(self, fcb, groupMask):
		"""Set FREEZE-mode on the specified groupMask.
		If groupMask is 0, all slaves are addressed."""

		self.__syncFreezeHelper(fcb, groupMask, DpTelegram_GlobalControl.CCMD_FREEZE)

	def freezeModeCancel(self, fcb, groupMask):
		"""Cancel FREEZE-mode on the specified groupMask.
		If groupMask is 0, all slaves are addressed."""

		self.__syncFreezeHelper(fcb, groupMask, DpTelegram_GlobalControl.CCMD_UNFREEZE)

class DPM1(DpMaster):
	def __init__(self, phy, masterAddr, debug=False):
		DpMaster.__init__(self, dpmClass=1, phy=phy,
			masterAddr=masterAddr,
			debug=debug)

class DPM2(DpMaster):
	def __init__(self, phy, masterAddr, debug=False):
		DpMaster.__init__(self, dpmClass=2, phy=phy,
			masterAddr=masterAddr,
			debug=debug)
