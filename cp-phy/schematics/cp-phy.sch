EESchema Schematic File Version 2  date Sun 02 Jun 2013 09:54:51 PM CEST
LIBS:power
LIBS:device
LIBS:transistors
LIBS:conn
LIBS:linear
LIBS:regul
LIBS:74xx
LIBS:cmos4000
LIBS:adc-dac
LIBS:memory
LIBS:xilinx
LIBS:special
LIBS:microcontrollers
LIBS:dsp
LIBS:microchip
LIBS:analog_switches
LIBS:motorola
LIBS:texas
LIBS:intel
LIBS:audio
LIBS:interface
LIBS:digital-audio
LIBS:philips
LIBS:display
LIBS:cypress
LIBS:siliconi
LIBS:opto
LIBS:atmel
LIBS:contrib
LIBS:valves
LIBS:raspberrypi
LIBS:rs485-rs232
LIBS:crystalosc
LIBS:cp-phy-cache
EELAYER 25  0
EELAYER END
$Descr A4 11700 8267
encoding utf-8
Sheet 1 1
Title "Raspberry Pi / Profibus DP / CP-PHY"
Date "2 jun 2013"
Rev "1.0"
Comp "Michael Buesch <m@bues.ch>"
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
Connection ~ 1600 5050
Wire Wire Line
	1700 5050 1500 5050
Wire Wire Line
	5300 4000 5000 4000
Connection ~ 4350 4300
Wire Wire Line
	4350 4300 4350 4000
Wire Wire Line
	4350 4000 4600 4000
Wire Wire Line
	4800 3450 3600 3450
Wire Wire Line
	7150 2150 7150 2700
Wire Wire Line
	7150 2150 3850 2150
Wire Wire Line
	3850 2150 3850 3050
Wire Wire Line
	7650 1950 4050 1950
Wire Wire Line
	9350 2050 9350 2700
Wire Wire Line
	3850 3050 3600 3050
Wire Wire Line
	5850 6050 9700 6050
Wire Wire Line
	9700 6050 9700 4750
Wire Wire Line
	9700 4750 9150 4750
Wire Wire Line
	9150 4650 9900 4650
Wire Wire Line
	9900 4650 9900 6550
Wire Wire Line
	9900 6550 5850 6550
Wire Wire Line
	5850 6150 10100 6150
Wire Wire Line
	10100 6150 10100 4550
Wire Wire Line
	10100 4550 9150 4550
Wire Wire Line
	3950 3150 3950 1850
Wire Wire Line
	4450 5950 3250 5950
Wire Wire Line
	3250 5950 3250 6600
Wire Wire Line
	3250 6600 2500 6600
Wire Wire Line
	4300 6450 4450 6450
Wire Wire Line
	9050 950  9200 950 
Wire Wire Line
	3600 4650 7550 4650
Wire Wire Line
	4750 3150 4800 3150
Wire Wire Line
	3950 3150 3600 3150
Wire Wire Line
	3600 3350 4150 3350
Wire Wire Line
	7500 950  7650 950 
Wire Wire Line
	9950 4350 9950 3850
Wire Wire Line
	9950 4350 9750 4350
Wire Wire Line
	9150 4050 10150 4050
Wire Wire Line
	9150 3850 9350 3850
Wire Wire Line
	3600 4450 4200 4450
Wire Wire Line
	4200 4450 4200 4750
Wire Wire Line
	7300 4350 7550 4350
Wire Wire Line
	7300 3850 7550 3850
Wire Wire Line
	1600 5050 1600 5150
Wire Wire Line
	1600 5150 1700 5150
Wire Wire Line
	1500 2850 1700 2850
Wire Wire Line
	1700 3150 1600 3150
Wire Wire Line
	1600 3150 1600 2850
Connection ~ 1600 2850
Wire Wire Line
	7300 3450 7550 3450
Wire Wire Line
	7300 3950 7550 3950
Wire Wire Line
	9150 4350 9350 4350
Wire Wire Line
	9950 3850 9750 3850
Connection ~ 9950 4050
Wire Wire Line
	10150 3450 9150 3450
Wire Wire Line
	7500 1350 7650 1350
Wire Wire Line
	3600 3250 4050 3250
Wire Wire Line
	4050 3250 4050 1950
Wire Wire Line
	6200 3450 6250 3450
Wire Wire Line
	3600 4550 7550 4550
Wire Wire Line
	4200 4750 7550 4750
Wire Wire Line
	4000 6350 4450 6350
Wire Wire Line
	2500 6900 2650 6900
Wire Wire Line
	2500 6500 3350 6500
Wire Wire Line
	3350 6500 3350 6050
Wire Wire Line
	3350 6050 4450 6050
Wire Wire Line
	4150 3350 4150 2050
Wire Wire Line
	9350 2050 9050 2050
Wire Wire Line
	5850 6350 6000 6350
Wire Wire Line
	3950 1850 7650 1850
Wire Wire Line
	4150 2050 7650 2050
Wire Wire Line
	9350 2700 7150 2700
Wire Wire Line
	3600 4300 4550 4300
Wire Wire Line
	5300 4300 5050 4300
Text GLabel 5300 4300 2    60   Input ~ 0
3.3V
Text GLabel 5300 4000 2    60   Input ~ 0
GND
$Comp
L C C3
U 1 1 51ABA0EA
P 4800 4000
F 0 "C3" H 4850 4100 50  0000 L CNN
F 1 "47pF" H 4850 3900 50  0000 L CNN
	1    4800 4000
	0    -1   -1   0   
$EndComp
$Comp
L R R1
U 1 1 51ABA0DD
P 4800 4300
F 0 "R1" V 4880 4300 50  0000 C CNN
F 1 "10k" V 4800 4300 50  0000 C CNN
	1    4800 4300
	0    -1   -1   0   
$EndComp
NoConn ~ 9150 4850
Text GLabel 6000 6350 2    60   Input ~ 0
GND
NoConn ~ 5850 6250
Text Notes 8950 2600 2    120  ~ 0
Raspberry Pi
Text Notes 2750 7350 2    120  ~ 0
PROFIBUS DP
NoConn ~ 9050 2150
NoConn ~ 2500 6800
NoConn ~ 2500 6700
NoConn ~ 2500 6200
NoConn ~ 2500 6400
NoConn ~ 2500 6300
NoConn ~ 2500 6100
Text GLabel 2650 6900 2    60   Input ~ 0
GND
Text GLabel 4000 6350 0    60   Input ~ 0
GND
Text GLabel 4300 6450 0    60   Input ~ 0
5V
Text GLabel 9200 950  2    60   Input ~ 0
5V
$Comp
L DB9 J1
U 1 1 51AB8DF1
P 2050 6500
F 0 "J1" H 2050 7050 70  0000 C CNN
F 1 "DB9" H 2050 5950 70  0000 C CNN
	1    2050 6500
	-1   0    0    1   
$EndComp
Text GLabel 6250 3450 2    60   Input ~ 0
3.3V
Text GLabel 4750 3150 0    60   Input ~ 0
GND
$Comp
L CRYSTALOSC X1
U 1 1 51AB8751
P 5500 3300
F 0 "X1" H 5500 3000 60  0000 C CNN
F 1 "20 MHz Osc" H 5500 3300 60  0000 C CNN
	1    5500 3300
	-1   0    0    1   
$EndComp
NoConn ~ 3600 5150
NoConn ~ 3600 5050
NoConn ~ 3600 4950
NoConn ~ 3600 4850
NoConn ~ 3600 4750
NoConn ~ 3600 4200
NoConn ~ 3600 4100
NoConn ~ 3600 4000
NoConn ~ 3600 3900
NoConn ~ 3600 3800
NoConn ~ 3600 3700
NoConn ~ 3600 3550
NoConn ~ 3600 2950
NoConn ~ 3600 2850
NoConn ~ 9050 1950
NoConn ~ 9050 1850
NoConn ~ 9050 1750
NoConn ~ 9050 1650
NoConn ~ 9050 1550
NoConn ~ 9050 1450
NoConn ~ 9050 1350
NoConn ~ 9050 1250
NoConn ~ 9050 1150
NoConn ~ 9050 1050
NoConn ~ 7650 2150
NoConn ~ 7650 1750
NoConn ~ 7650 1650
NoConn ~ 7650 1550
NoConn ~ 7650 1450
NoConn ~ 7650 1250
NoConn ~ 7650 1150
NoConn ~ 7650 1050
Text GLabel 7500 1350 0    60   Input ~ 0
GND
Text GLabel 7500 950  0    60   Input ~ 0
3.3V
Text GLabel 10150 3450 2    60   Input ~ 0
3.3V
Text GLabel 10150 4050 2    60   Input ~ 0
GND
$Comp
L C C5
U 1 1 51AB85B8
P 9550 4350
F 0 "C5" H 9600 4450 50  0000 L CNN
F 1 "1µF" H 9600 4250 50  0000 L CNN
	1    9550 4350
	0    -1   -1   0   
$EndComp
$Comp
L C C2
U 1 1 51AB85A8
P 9550 3850
F 0 "C2" H 9600 3950 50  0000 L CNN
F 1 "1µF" H 9600 3750 50  0000 L CNN
	1    9550 3850
	0    -1   -1   0   
$EndComp
$Comp
L C C4
U 1 1 51AB855C
P 7300 4150
F 0 "C4" H 7350 4250 50  0000 L CNN
F 1 "1µF" H 7350 4050 50  0000 L CNN
	1    7300 4150
	1    0    0    -1  
$EndComp
$Comp
L C C1
U 1 1 51AB8556
P 7300 3650
F 0 "C1" H 7350 3750 50  0000 L CNN
F 1 "1µF" H 7350 3550 50  0000 L CNN
	1    7300 3650
	1    0    0    -1  
$EndComp
NoConn ~ 7550 4850
Text GLabel 1500 5050 0    60   Input ~ 0
GND
NoConn ~ 1700 3450
Text GLabel 1500 2850 0    60   Input ~ 0
3.3V
$Comp
L MAX232 U1
U 1 1 51AB7886
P 8350 4150
F 0 "U1" H 8350 5000 70  0000 C CNN
F 1 "MAX3232" H 8350 3300 70  0000 C CNN
	1    8350 4150
	1    0    0    -1  
$EndComp
$Comp
L RS485-RS232 U2
U 1 1 51AB772F
P 5150 6550
F 0 "U2" H 5150 7350 60  0000 C CNN
F 1 "RS485-RS232" H 5150 6150 60  0000 C CNN
	1    5150 6550
	1    0    0    -1  
$EndComp
$Comp
L RPI2-P1 P1
U 1 1 51AB5DB7
P 8350 1550
F 0 "P1" H 8350 2350 60  0000 C CNN
F 1 "RPI2-P1" H 8350 750 60  0000 C CNN
	1    8350 1550
	1    0    0    -1  
$EndComp
$Comp
L ATMEGA88PA-P IC1
U 1 1 51AB3DFD
P 2600 3950
F 0 "IC1" H 1900 5200 50  0000 L BNN
F 1 "ATMEGA88PA-P" H 2800 2550 50  0000 L BNN
F 2 "DIL28" H 2000 2600 50  0001 C CNN
	1    2600 3950
	1    0    0    -1  
$EndComp
$EndSCHEMATC
