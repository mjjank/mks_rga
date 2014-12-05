from RGA import *
from threading import Thread
import time
global switch
switch=0

RGA_eh1=RGA("rga-id03-eh1",10014)

#RGA_eh1.filament("On")


#RGA_eh1.scanStart()
time.sleep(1)
t1 = Thread(target=RGA_eh1.peakScan, args=("18 28 44",))

t1.start()
time.sleep(2)


	


n=0
while True:
	print RGA_eh1.read_oneMass(18) , RGA_eh1.read_oneMass(44) 
	time.sleep(0.2)
	#print RGA_eh1.status
	n=n+1
	if n==60:		
		break

RGA_eh1.scan=False


while t1.isAlive():
	
	if t1.isAlive()==False:
		print "Scan process stoped ..."	
	pass
#RGA_eh1.filament("Off")
RGA_eh1.release()
