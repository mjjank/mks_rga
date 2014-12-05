import sys
import telnetlib

# Connecting to RGA - RGA(HOST,PORT)
class RGA:	
	
	
	def __init__(self,HOST,PORT):
		
		print "Startin connection with RGA: "			
		self.telCon=telnetlib.Telnet(HOST,PORT)
		print self.telCon.read_until("\r\r")
		
		print "List of avalible sensors: "
		self.telCon.write("Sensors\n")
		out=self.telCon.read_until("\r\r")
		print out
		
		out=out.replace("\r","")	#Removing \r, \n form the output
		out=out.replace("\n","")
		out=out.split(' ')		
		out=filter(None,out)		#Removing empty fields
		
		print "Selectin sensor: "
		sensor= "Select " + out[7] + "\n"	 
		self.telCon.write(sensor)
		print self.telCon.read_until("\r\r")
		
		print "Taking control over the sensor: "
		self.telCon.write("Control \"RGA python server\" \"1.0\" \n")
		print self.telCon.read_until("\r\r")
	
	def release(self):
		
		print "Release of the sensor: "
		self.telCon.write("Release\n")
		print self.telCon.read_until("\r\r")
		
