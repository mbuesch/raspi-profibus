#!/usr/bin/env python3
#
# Simple pyprofibus example
#
# This example initializes an ET-200S slave, reads input
# data and writes the data back to the module.
#
# The hardware configuration is as follows:
#
#   v--------------v----------v----------v----------v----------v
#   |     IM 151-1 | PM-E     | 2 DO     | 2 DO     | 4 DI     |
#   |     STANDARD | DC24V    | DC24V/2A | DC24V/2A | DC24V    |
#   |              |          |          |          |          |
#   |              |          |          |          |          |
#   | ET 200S      |          |          |          |          |
#   |              |          |          |          |          |
#   |              |          |          |          |          |
#   |       6ES7   | 6ES7     | 6ES7     | 6ES7     | 6ES7     |
#   |       151-   | 138-     | 132-     | 132-     | 131-     |
#   |       1AA04- | 4CA01-   | 4BB30-   | 4BB30-   | 4BD01-   |
#   |       0AB0   | 0AA0     | 0AA0     | 0AA0     | 0AA0     |
#   ^--------------^----------^----------^----------^----------^
#

import pyprofibus


# Enable verbose debug messages?
debug = True

# Create a PHY (layer 1) interface object
phy = pyprofibus.CpPhy(debug=debug)

# Create a DP class 1 master with DP address 1
master = pyprofibus.DPM1(phy = phy,
			 masterAddr = 1,
			 debug = debug)

# Create a slave description for an ET-200S.
# The ET-200S has got the DP address 8 set via DIP-switches.
et200s = pyprofibus.DpSlaveDesc(identNumber = 0x817A,
				slaveAddr = 3,
				inputAddressRangeSize = 22,
				outputAddressRangeSize = 6)

# Create Chk_Cfg telegram elements
for elem in (\
				pyprofibus.DpCfgDataElement(0xC1),		# 1 In-Byte & 1 Out-Byte follows
				pyprofibus.DpCfgDataElement(0x06-1),	# DI 22 Bytes
				pyprofibus.DpCfgDataElement(0x16-1),	# DO  6 Bytes
				pyprofibus.DpCfgDataElement(0x00)):		# 
			et200s.chkCfgTelegram.addCfgDataElement(elem)

# Set User_Prm_Data
et200s.setPrmTelegram.addUserPrmData([0x03,0x02,0x07,0x00,0x00])

# Set various standard parameters
et200s.setSyncMode(False)		# Sync-mode not supported
et200s.setFreezeMode(False)		# Freeze-mode not supported
et200s.setGroupMask(1)			# Group-ident 1
et200s.setWatchdog(1000)		# Watchdog: 1 second

# Register the ET-200S slave at the DPM
master.addSlave(et200s)

try:
	# Initialize the DPM and all registered slaves
	master.initialize()
	print("Initialization finished. Running Data_Exchange...")

	# Cyclically run Data_Exchange.
	# 4 input bits from the 4-DI module are copied to
	# the two 2-DO modules.
	inData = [0]*et200s.inputAddressRangeSize
	outData = [0]*et200s.outputAddressRangeSize
	while 1:
		#outData = [inData & 3, (inData >> 2) & 3]
		inData = master.dataExchange(da = et200s.slaveAddr,
					     outData = outData)
		#inData = inData[0] if inData else 0
except:
	print("Terminating.")
	master.destroy()
	raise
