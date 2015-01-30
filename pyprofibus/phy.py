#
# PROFIBUS DP - Communication Processor PHY access library
#
# Copyright (c) 2013-2014 Michael Buesch <m@bues.ch>
#
# Licensed under the terms of the GNU General Public License version 2,
# or (at your option) any later version.
#

import time
import sys

from pyprofibus.util import *

try:
	from spidev import SpiDev
except ImportError as e:
	sys.stderr.write("Failed to import module SpiDev:\n%s\n" % str(e))
try:
	import RPi.GPIO as GPIO
except ImportError as e:
	sys.stderr.write("Failed to import module RPi.GPIO:\n%s\n" % str(e))


class PhyError(ProfibusError):
	pass

class CpPhyMessage(object):
	RASPI_PACK_HDR_LEN	= 3

	# Message frame control
	RPI_PACK_NOP		= 0	# No operation
	RPI_PACK_RESET		= 1	# Reset
	RPI_PACK_SETCFG		= 2	# Set config
	RPI_PACK_PB_SRD		= 3	# Profibus SRD request
	RPI_PACK_PB_SRD_REPLY	= 4	# Profibus SRD reply
	RPI_PACK_PB_SDN		= 5	# Profibus SDN request
	RPI_PACK_ACK		= 6	# Short ACK
	RPI_PACK_NACK		= 7	# Short NACK
	__RPI_PACK_FC_MAX	= RPI_PACK_NACK

	fc2name = {
		RPI_PACK_NOP		: "NOP",
		RPI_PACK_RESET		: "RESET",
		RPI_PACK_SETCFG		: "SETCFG",
		RPI_PACK_PB_SRD		: "PB_SRD",
		RPI_PACK_PB_SRD_REPLY	: "PB_SRD_REPLY",
		RPI_PACK_PB_SDN		: "PB_SDN",
		RPI_PACK_ACK		: "ACK",
		RPI_PACK_NACK		: "NACK",
	}

	def __init__(self, fc, payload=()):
		self.fc = fc
		self.payload = payload

	@staticmethod
	def calculateChecksum(packetData):
		return ((sum(packetData) - (packetData[2] & 0xFF)) ^ 0xFF) & 0xFF

	def getRawData(self):
		data = [ self.fc, len(self.payload), 0, ]
		data.extend(self.payload)
		data[2] = self.calculateChecksum(data)
		return data

	def setRawData(self, data):
		self.fc = data[0]
		if self.fc == self.RPI_PACK_NOP:
			return
		if len(data) < self.RASPI_PACK_HDR_LEN:
			raise PhyError("CpPhyMessage: Message too small")
		if self.calculateChecksum(data) != data[2]:
			raise PhyError("CpPhyMessage: Invalid checksum 0x%02X in: %s" %\
				(data[2], str(self)))
		self.payload = data[3:]
		if self.fc < 0 or self.fc > self.__RPI_PACK_FC_MAX:
			raise PhyError("CpPhyMessage: Unknown frame control 0x%02X" %\
				self.fc)
		if len(self.payload) != data[1]:
			raise PhyError("CpPhyMessage: Invalid payload length")

	def __repr__(self):
		try:
			fcname = self.fc2name[self.fc]
		except KeyError:
			fcname = "0x%02X" % self.fc
		return "CpPhyMessage(fc=%s, payload=[%s])" %\
			(fcname,
			 ", ".join("0x%02X" % d for d in self.payload))

class CpPhy(object):
	# Profibus baud-rates
	PB_PHY_BAUD_9600	= 0
	PB_PHY_BAUD_19200	= 1
	PB_PHY_BAUD_45450	= 2
	PB_PHY_BAUD_93750	= 3
	PB_PHY_BAUD_187500	= 4
	PB_PHY_BAUD_500000	= 5
	PB_PHY_BAUD_1500000	= 6
	PB_PHY_BAUD_3000000	= 7
	PB_PHY_BAUD_6000000	= 8
	PB_PHY_BAUD_12000000	= 9

	# RTS mode
	PB_PHY_RTS_ALWAYS_LO	= 0
	PB_PHY_RTS_ALWAYS_HI	= 1
	PB_PHY_RTS_SENDING_HI	= 2
	PB_PHY_RTS_SENDING_LO	= 3

	# GPIO numbers (BCM)
	GPIO_RESET		= 17
	GPIO_IRQ		= 27
	GPIO_SS			= 8
	GPIO_MISO		= 9
	GPIO_MOSI		= 10
	GPIO_SCK		= 11

	baud2id = {
		9600		: PB_PHY_BAUD_9600,
		19200		: PB_PHY_BAUD_19200,
		45450		: PB_PHY_BAUD_45450,
		93750		: PB_PHY_BAUD_93750,
		187500		: PB_PHY_BAUD_187500,
		500000		: PB_PHY_BAUD_500000,
		1500000		: PB_PHY_BAUD_1500000,
		3000000		: PB_PHY_BAUD_3000000,
		6000000		: PB_PHY_BAUD_6000000,
		12000000	: PB_PHY_BAUD_12000000,
	}

	def __init__(self, device=0, chipselect=0, debug=False):
		self.device = device
		self.chipselect = chipselect
		self.debug = debug

		try:
			try:
				# Initialize GPIOs
				GPIO.setmode(GPIO.BCM) # Use Broadcom numbers
				GPIO.setwarnings(False)
				GPIO.setup(self.GPIO_RESET, GPIO.OUT, initial=GPIO.LOW)
				GPIO.setup(self.GPIO_IRQ, GPIO.IN, pull_up_down=GPIO.PUD_OFF)
				GPIO.add_event_detect(self.GPIO_IRQ, GPIO.RISING)
				time.sleep(0.05)
			except RuntimeError as e:
				raise PhyError("Failed to initialize GPIOs: %s" %\
					str(e))

			# Initialize SPI
			try:
				self.spi = SpiDev()
				self.spi.open(device, chipselect)
			except IOError as e:
				raise PhyError("Failed to open SPI device %d.%d: %s" %\
					(device, chipselect, str(e)))
			try:
				self.spi.mode = 0;
				self.spi.bits_per_word = 8;
				self.spi.cshigh = False
				self.spi.lsbfirst = False
				self.spi.max_speed_hz = 200000;
			except IOError as e:
				try:
					self.spi.close()
					self.spi = None
				except:
					pass
				raise PhyError("Failed to configure SPI device %d.%d: %s" %\
					(device, chipselect, str(e)))

			# Get the controller out of hardware reset
			GPIO.output(self.GPIO_RESET, GPIO.HIGH)
			time.sleep(0.2)

			# Send a software reset
			self.sendReset()
			# Upload default config
			self.profibusSetPhyConfig()
		except:
			GPIO.cleanup()
			raise

	def cleanup(self):
		self.spi.close()
		self.spi = None
		GPIO.cleanup()

	# Poll for received packet.
	# timeout => In seconds. 0 = none, Negative = unlimited.
	def poll(self, timeout=0):
		limit = TimeLimited(timeout)
		while GPIO.event_detected(self.GPIO_IRQ):
			if limit.exceed():
				return None
			limit.sleep(0.001)
		limit.add(0.5)
		while not limit.exceed():
			fc = self.spi.readbytes(1)[0]
			if fc != CpPhyMessage.RPI_PACK_NOP:
				break
		else:
			return None
		reply = [ fc ]
		reply.extend(self.spi.readbytes(CpPhyMessage.RASPI_PACK_HDR_LEN - 1))
		payloadLen = reply[1] & 0xFF
		if payloadLen:
			reply.extend(self.spi.readbytes(payloadLen))
		message = CpPhyMessage(0)
		message.setRawData(reply)
		if self.debug:
			print("[PHY] received message:", message)
		return message

	def __sendMessage(self, message):
		if self.debug:
			print("[PHY] sending message:", message)
		self.spi.writebytes(message.getRawData())

	def sendReset(self):
		self.__sendMessage(CpPhyMessage(CpPhyMessage.RPI_PACK_RESET))
		reply = self.poll(timeout=-1)
		if reply.fc != CpPhyMessage.RPI_PACK_ACK:
			raise PhyError("Failed to reset PHY")

	def profibusSetPhyConfig(self, baudrate=19200,
				 rxTimeoutMs=100,
				 bitErrorChecks=True,
				 rtsMode=PB_PHY_RTS_ALWAYS_LO):
		try:
			baudID = self.baud2id[baudrate]
		except KeyError:
			raise PhyError("Invalid baud-rate")
		if rxTimeoutMs < 1 or rxTimeoutMs > 255:
			raise PhyError("Invalid RX timeout")
		payload = [ baudID,
			    rxTimeoutMs,
			    1 if bitErrorChecks else 0,
			    rtsMode & 0xFF ]
		message = CpPhyMessage(CpPhyMessage.RPI_PACK_SETCFG, payload)
		self.__sendMessage(message)
		reply = self.poll(timeout=-1)
		if reply.fc != CpPhyMessage.RPI_PACK_ACK:
			raise PhyError("Failed to upload config")

	def profibusSend_SDN(self, telegramData):
		self.__sendMessage(CpPhyMessage(CpPhyMessage.RPI_PACK_PB_SDN,
						telegramData))

	def profibusSend_SRD(self, telegramData):
		self.__sendMessage(CpPhyMessage(CpPhyMessage.RPI_PACK_PB_SRD,
						telegramData))
