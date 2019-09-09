#!/usr/bin/python

#####################################################################################
# pico_status.py
# author 		: Kyriakos Naziris
# modified by 		: Siewert Lameijer aka Siewert308SW
# modified by		: janmagnet
# since			: 31-12-2016
# updated		: 10-06-2019
# Script to show you some statistics pulled from your UPS PIco HV3.0A/B/B+

# -*- coding: utf-8 -*-
# improved and completed by PiModules Version 1.0 29.08.2015
# picoStatus-v3.py by KTB is based on upisStatus.py by Kyriakos Naziris
# Kyriakos Naziris / University of Portsmouth / kyriakos@naziris.co.uk
#
# Improved and modified for PiModules PIco HV3.0A Stack Plus / Plus / Top
# by Siewert Lameijer aka Siewert308SW
#
# Improved for PiModules PIco HV3.0B/B+ by janmagnet
#
# Improved by adding system information (SysInfo) from register 0x69 0x28 word
# this reports back the 4 digit code
# see Table 9 UPS PIco HV3.0 HAT SysInfo PIco Register in the manual
# note that this register needs to be manually reset using sudo "i2cset -y 1 0x69 0x28 0x0000 w"
# by MMinehan
# 
#
#####################################################################################

#####################################################################################
# SETTINGS
#####################################################################################

# Set your desired temperature symbol
# C = Celsius
# F = Fahrenheit
degrees = "C"

# Do you have a PIco FAN kit installed?
# True or False
fankit = True

# Do you have a to92 temp sensor installed?
# True or False
to92 = True

# Do you have extended power?
# True or False
extpwr = False

#####################################################################################
# It's not necessary to edit anything below, unless you're knowing what to do!
#####################################################################################

import os
import smbus
import time
import datetime

i2c = smbus.SMBus(1)

def fw_version():
   time.sleep(0.1)
   data = i2c.read_byte_data(0x69, 0x26)
   data = format(data,"02x")
   return data
   
def boot_version():
   time.sleep(0.1)
   data = i2c.read_byte_data(0x69, 0x25)
   data = format(data,"02x")
   return data

def pcb_version():
   time.sleep(0.1)
   data = i2c.read_byte_data(0x69, 0x24)
   data = format(data,"02x")
   return data    

def pwr_mode():
   data = i2c.read_byte_data(0x69, 0x00)
   data = data & ~(1 << 7)
   if (data == 1):
      return "RPi POWERED"
   elif (data == 2):
      return "BAT POWERED"
   else:
      return "ERROR"
	  
def bat_version():
   time.sleep(0.1)
   data = i2c.read_byte_data(0x6b, 0x07)
   if (data == 0x46):
      return "LiFePO4 (ASCII : F) used in version Stack/Top-End"
   elif (data == 0x51):
      return "LiFePO4 (ASCII : Q) used in version Plus/Advanced"
   elif (data == 0x53):
      return "LiPO (ASCII: S) used in version Stack/Top-End"
   elif (data == 0x50):
      return "LiPO (ASCII: P) used in version Plus/Advanced"
   elif (data == 0x49):
      return "Li-Ion ASCII : I) used in version Stack/Top-End"
   elif (data == 0x4f):
      return "Li-Ion (ASCII : O) used in version Plus/Advanced"
   elif (data == 0x48):
      return "NiMH (ASCII : H) used in version Stack/Top-End"
   elif (data == 0x4d):
      return "NiMH (ASCII : M) used in version Plus/Advanced"
   elif (data == 0x4c):
      return "SAL (ASCII : L) used in version Stack/Top-End"
   elif (data == 0x41):
      return "SAL (ASCII : A) used in version Plus/Advanced"
   else:
      return "ERROR"
	  
def bat_runtime():
   time.sleep(0.1)
   data = i2c.read_byte_data(0x6b, 0x01) + 1
   if (data == 0x100):
      return "TIMER DISABLED"
   elif (data == 0xff):
      return "TIMER DISABLED"	  
   else:
      data = str(data)+ " MIN"
      return data	  
   
def bat_level():
   time.sleep(0.1)
   data = i2c.read_word_data(0x69, 0x08)
   data = format(data,"02x")
   return (float(data) / 100)
   
def bat_percentage():
   time.sleep(0.1)
   datavolts = bat_level()
   databattery = bat_version()
   if (databattery == "LiFePO4 (ASCII : F) used in version Stack/Top-End") or (databattery == "LiFePO4 (ASCII : Q) used in version Plus/Advanced"):
		databatminus = datavolts-2.90
		return int (((databatminus/0.70))*100)
   elif (databattery == "LiPO (ASCII: S) used in version Stack/Top-End") or (databattery == "LiPO (ASCII: P) used in version Plus/Advanced"):
		databatminus = datavolts-3.4
		return int (((databatminus/0.899))*100)
   return "N/A"
   
   
def charger_state():
   time.sleep(0.1)
   data = i2c.read_byte_data(0x69, 0x20)
   battpercentage = bat_percentage() 
   powermode = pwr_mode()
   databattery = bat_version()
   if (databattery == "LiFePO4 (ASCII : F) used in version Stack/Top-End") or (databattery == "LiFePO4 (ASCII : Q) used in version Plus/Advanced"):
	 if (data == 0x00) and (powermode == "BAT POWERED"):		
		return "DISCHARGING"
	 if (data == 0x01) and (powermode == "RPi POWERED"):	
		return "CHARGING"
	 if (data == 0x00) and (powermode == "RPi POWERED"):		
		return "CHARGED"		
   if (databattery == "LiPO (ASCII: S) used in version Stack/Top-End") or (databattery == "LiPO (ASCII: P) used in version Plus/Advanced"):
     if (data == 0x00) and (powermode == "BAT POWERED"):
		return "DISCHARGING"   
     if (data == 0x00) and (powermode == "RPi POWERED"):
		return "CHARGED" 	 
     if (data == 0x01) and (powermode == "RPi POWERED"):
		return "CHARGING" 

def rpi_level():
   time.sleep(0.1)
   data = i2c.read_word_data(0x69, 0x0a)
   data = format(data,"02x")
   powermode = pwr_mode()
   if (powermode == "RPi POWERED"):
		return (float(data) / 100)
   else:
		return "0.0"

def rpi_cpu_temp():
   time.sleep(0.1)
   data = os.popen('vcgencmd measure_temp').readline()
   data = (data.replace("temp=","").replace("'C\n",""))	
   if (degrees == "C"):
	return data
   elif (degrees == "F"):
	return (float(data) * 9 / 5) + 32
	
def ntc1_temp():
   time.sleep(0.1)
   data = i2c.read_byte_data(0x69, 0x1b)
   data = format(data,"02x")
   if (degrees == "C"):
	return data
   elif (degrees == "F"):
	return (float(data) * 9 / 5) + 32
	
def to92_temp():
   time.sleep(0.1)
   data = i2c.read_byte_data(0x69, 0x1C)
   data = format(data,"02x")
   if (degrees == "C"):
	return data
   elif (degrees == "F"):
	return (float(data) * 9 / 5) + 32

def epr_read():
   time.sleep(0.1)
   data = i2c.read_byte_data(0x69, 0x0c)
   data = format(data,"02x")
   return (float(data) / 100)
   
def sys_info():
   time.sleep(0.1)
   data = i2c.read_word_data(0x69, 0x28)
   data = format(data,"04x")
   return (data)

def ad2_read():
   time.sleep(0.1)
   data = i2c.read_byte_data(0x69, 0x07)
   data = format(data,"02x")
   return (float(data) / 100)
   
def fan_mode():
   time.sleep(0.1)
   data = i2c.read_byte_data(0x6b, 0x11)
   data = data & ~(1 << 2)
   if (data == 2):
      return "AUTOMATIC"  
   elif (data == 1):
      return "ON"
   elif (data == 0):
      return "OFF"
   else:
      return "ERROR" 	  

def fan_speed():
   time.sleep(0.1)
   data = i2c.read_byte_data(0x6b, 0x12)
   data = format(data,"02x")
   return int (float(data) * 100)

def fan_threshold():
   time.sleep(0.1)
   data = i2c.read_byte_data(0x6B, 0x14)
   data = format(data,"02x")
   if (degrees == "C"):
	return data
   elif (degrees == "F"):
	return (float(data) * 9 / 5) + 32
   
def rs232_state():
   time.sleep(0.1)  
   data = i2c.read_byte_data(0x6b, 0x02)
   if (data == 0x00):
      return "OFF"
   elif (data == 0xff):
      return "OFF"	  
   elif (data == 0x01):
      return "ON @ 4800 pbs"
   elif (data == 0x02):
      return "ON @ 9600 pbs"
   elif (data == 0x03):
      return "ON @ 19200 pbs"
   elif (data == 0x04):
      return "ON @ 34600 pbs"
   elif (data == 0x05):
      return "ON @ 57600 pbs"
   elif (data == 0x0f):
      return "ON @ 115200 pbs"	  
   else:
      return "ERROR"   
   
print " "
print "**********************************************"
print "*      	 UPS PIco HV3.0A/B/B+ Status        *"
print "*      	         Version 7.0                *"
print "**********************************************"
print " "
print " ","- PIco Firmware..........:",fw_version()
print " ","- PIco Bootloader........:",boot_version()
print " ","- PIco PCB Version.......:",pcb_version()
print " ","- PIco BAT Version.......:",bat_version()
print " ","- PIco BAT Runtime.......:",bat_runtime()
print " ","- PIco rs232 State.......:",rs232_state()
print " "
print " ","- Powering Mode..........:",pwr_mode()
print " ","- Charger State..........:",charger_state()
print " ","- Battery Percentage.....:",bat_percentage(),"%"
print " ","- Battery Voltage........:",bat_level(),"V"
print " ","- RPi Voltage............:",rpi_level(),"V"
print " "

if (degrees == "C"): 
	print " ","- RPi CPU Temperature....:",rpi_cpu_temp(),"C"
	print " ","- NTC1 Temperature.......:",ntc1_temp(),"C"	
elif (degrees == "F"):
	print " ","- RPi CPU Temperature....:",rpi_cpu_temp(),"F"
	print " ","- NTC1 Temperature.......:",ntc1_temp(),"F"	
else:
	print " ","- RPi CPU Temperature....: please set temperature symbol in the script!"
	print " ","- NTC1 Temperature.......: please set temperature symbol in the script!"

if (to92 == True):
	if (degrees == "C"):
		print " ","- TO-92 Temperature......:",to92_temp(),"C"
	elif (degrees == "F"):
		print " ","- TO-92 Temperature......:",to92_temp(),"F"
	else:
		print " ","- TO-92 Temperature......: please set temperature symbol in the script!"
		
if (extpwr == True):	
	print " ","- Extended Voltage.......:",epr_read(),"V"
	print " ","- A/D2 Voltage...........:",ad2_read(),"V"

if (fankit == True):		
	print " "
if (fan_mode() == "AUTOMATIC"):
	print " ","- PIco FAN Mode..........:",fan_mode()	
	if (degrees == "C"):
		print " ","- PIco FAN Temp Threshold:",fan_threshold(),"C"
	elif (degrees == "F"):
		print " ","- PIco FAN Temp Threshold:",fan_threshold(),"F"
	else:
		print " ","- PIco FAN Temp Threshold: please set temperature symbol in the script!"	
else:
	print " ","- PIco FAN Mode..........:",fan_mode()
	if (fan_mode() == "ON"):	
		print " ","- PIco FAN Speed.........:",fan_speed(),"RPM"  
	else:
		print " ","- PIco FAN Speed.........: 0 RPM"	
	
	if (degrees == "C"):
		print " ","- PIco FAN Temp Threshold:",fan_threshold(),"C"
	elif (degrees == "F"):
		print " ","- PIco FAN Temp Threshold:",fan_threshold(),"F"
	else:
		print " ","- PIco FAN Temp Threshold: please set temperature symbol in the script!"	

print " ","- System Information.....:",sys_info()

print " "
print "**********************************************"
print "*           Powered by PiModules             *"
print "**********************************************"
print " "
