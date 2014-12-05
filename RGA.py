import sys
import telnetlib
import time
import numpy
# Connecting to RGA - RGA(HOST,PORT)
class RGA:	
	
	scan = True		#This is used for stoping peak scan - if set to False
	status ="Idle"		#Status of the device
	showReadout=True	#This one supresses or not text output from RGA
	
####Class constructor
	def __init__(self,HOST,PORT):

		
		
		print "Starting connection with RGA: "			
		self.telCon=telnetlib.Telnet(HOST,PORT)
		#print self.telCon.read_until("\r\r")
		self.readout(0,True)		

		print "List of avalible sensors: "
		self.telCon.write("Sensors\n")
		out=self.readout(0,True)

		out=out.replace("\r","")	#Removing \r, \n form the output
		out=out.replace("\n","")
		out=out.split(' ')		
		out=filter(None,out)		#Removing empty fields
		

		print "Status of sensors with RGA: "			
		self.telCon.write("SensorState\n")
		self.readout(0,True)		
	
		print "Selecting sensor: "
		sensor= "Select " + out[7] + "\n"	 
		self.telCon.write(sensor)
		self.readout(0,True)
		
		print "Taking control over the sensor: "
		self.telCon.write("Control \"RGA python server\" \"1.0\" \n")
		self.readout(0,True)
		
		self.status="Idle"
	

		
####Read output
	def readout(self,timeout,show):
		
				
		
		if self.showReadout==True and show==True and timeout==0:
			out=self.telCon.read_until("\r\r")
			print out
		elif self.showReadout==True and show==True and timeout > 0:
			out=self.telCon.read_until("\r\r",timeout)
			print out
		elif self.showReadout==False and timeout==0:
			out=self.telCon.read_until("\r\r")
		elif self.showReadout==False and timeout > 0:
			out=self.telCon.read_until("\r\r",timeout)		
		else:
			out="Readout error !!!!"
			print out
		return out
					
####Release
	def release(self):
		
		print "Release of the sensor: "
		self.telCon.write("Release\n")
		self.readout(1,True)
		
####Filament control
	def filament(self,state):
		
		if state=="On":
			self.telCon.write("FilamentControl On\n")
			time.sleep(5)
			self.readout(0,True)	#Little bit robust but works
			self.readout(0,True)
			self.readout(0,True)
		elif state=="Off":
			self.telCon.write("FilamentControl Off\n")
			time.sleep(5)
			self.readout(0,True)	#Little bit robust but works
			self.readout(0,True)
			self.readout(0,True)
			self.readout(0,True)
		else:
			print "Wrong input"
		
####Single peaks scan
	def peakScan(self,mass_selected):


		global mass_read
		mass_read=numpy.array([0, 0, 0])

		# Here we convert string to numbers- selecting masses to scan from input
		mass_selected=mass_selected.split(' ')
		mass_selected=[int(i) for i in mass_selected]
		print "Masses selected for scan :" , mass_selected, "\n"

		# Defininf peak jump scan
		print "Add peak jump measurement: "
		self.telCon.write("AddPeakJump Peak1 PeakCenter 2 0 0 0\n")
		self.readout(0,True)

		# Adding masses to scan
		for i in range(len(mass_selected)):	
					
				self.telCon.write("MeasurementAddMass "+str(mass_selected[i])+"\n") #Here we again conver number to string - just for training
				self.readout(0,True)
		time.sleep(1)
		# Adding scan to scan list 	
		self.telCon.write("ScanAdd Peak1\n")
		self.readout(0,True)
		
		#Starting scan
		self.telCon.write("ScanStart 1\n")
		

		self.status="Scanning"

		while (self.scan):
			
				
			# Processing output string 	
			out=self.telCon.read_until("\r\r",1)
			out=out.split(' ')
			out=filter(None,out)
			
			# If the list length is 3,  it corresponds to one of measured masses
			if len(out)==3 and out[0]=="MassReading":
				new_row=[time.time(), float(out[1]),float(out[2])] #The row is : time, mass number, mass pressure
				mass_read=numpy.vstack([mass_read,new_row]) #Adding measured value to array				
				if float(out[1])==mass_selected[-1]: # When last mass value of scan is read , restart scan
					self.telCon.write("ScanResume 1\n")
			
		#Stop scan	 
		self.telCon.write("ScanStop\n")			
		print self.telCon.read_until("nigdy",1) #Collect all garbage output
		print "Mass read stoped..."		
		self.status="Idle"
		self.scan=True

#####Read one mass 
	def read_oneMass(self,oneMass):
				
		find_mass=numpy.nonzero(mass_read==oneMass)
		mass_found=mass_read[find_mass[0],:]
		out=[int(mass_found[-1,0]), int(mass_found[-1,1]), mass_found[-1,2]]
		return out		
