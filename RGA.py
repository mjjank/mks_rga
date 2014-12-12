import time
import numpy
from rga_telnet import *
# Connecting to RGA - RGA(HOST,PORT)


class RGA:

	scan = True  # This is used for stop of peak scan - if set to False
	status = [0 for col in range(4)]  # Status of the device, look in rga_status method
	showReadout = True  # This one is responsible for the text output from RGA

	# Class constructor
	def __init__(self, host, port):

		print("Starting connection with RGA: ")
		self.rga_id03 = RgaTelnet(host, port)
		out = self.rga_readout(1, True)
		if out.find("MKSRGA  Single") > -1:
			self.status[0] = 1

		print("List of available sensors: ")
		self.rga_id03.write("Sensors\n")
		out = self.rga_readout(1, True)

		out = out.replace("\r", "")  # Removing \r, \n form the output
		out = out.replace("\n", "")
		out = out.split(' ')
		out[:] = (i for i in out if i != '')  # Removing empty fields

		print("Status of sensors with RGA: ")
		self.rga_id03.write("SensorState\n")
		self.rga_readout(1, True)

		print("Selecting sensor: ")
		sensor = "Select " + str(out[7]) + "\n"
		self.rga_id03.write(sensor)
		self.rga_readout(1, True)

		print("Taking control over the sensor: ")
		self.rga_id03.write("Control \"RGA python server\" \"1.0\" \n")
		out = self.rga_readout(1, True)
		if out.find("Control OK") > -1:
			self.status[1] = 1

	# Read output
	def rga_readout(self, timeout, show):
		out = "Nothing"
		print_output = self.showReadout and show
		if print_output:
			out = self.rga_id03.read("\r\r", timeout)
			print(out)
		elif print_output:
			out = self.rga_id03.read("\r\r", timeout)
		return out

	# Release
	def rga_release(self):

		print("Release of the sensor: ")

		self.rga_id03.write("Release\n")
		self.rga_readout(1, True)
		self.status[1] = 0
		self.status[0] = 0

	# Filament control
	def rga_filament(self, state):

		if state == "On":
			self.rga_id03.write("FilamentControl On\n")
			time.sleep(5)
			for i in range(3):
				self.rga_readout(1, True)  # Little bit robust but works

			self.status[2] = 1
		elif state == "Off":
			self.rga_id03.write("FilamentControl Off\n")
			time.sleep(5)
			for i in range(3):
				self.rga_readout(1, True)
			self.status[2] = 0
		else:
			print("Wrong filament input")

	# Single peaks scan
	def rga_peakscan(self, mass_selected):

		global mass_read
		mass_read = numpy.array([0, 0, 0])

		# Here we convert string to numbers- selecting masses to scan from input
		mass_selected = [int(i) for i in mass_selected]
		print("Masses selected for scan :", mass_selected, "\n")

		# Defining peak jump scan
		print("Add peak jump measurement: ")
		self.rga_id03.write("AddPeakJump Peak1 PeakCenter 2 0 0 0\n")
		self.rga_readout(1, True)

		# Adding masses to scan
		for i in range(len(mass_selected)):

				self.rga_id03.write("MeasurementAddMass " + str(mass_selected[i]) + "\n")  # Here we again convert number to string - just for training
				self.rga_readout(1, True)
		time.sleep(1)
		# Adding scan to scan list
		self.rga_id03.write("ScanAdd Peak1\n")
		self.rga_readout(1, True)

		# Starting scan
		self.rga_id03.write("ScanStart 1\n")

		self.status[3] = 1

		while self.scan:

			# Processing output string
			# out = self.rga_id03.read_until("\r\r", 1)
			out = self.rga_readout(1, True)
			out = out.split(' ')
			out[:] = (i for i in out if i != '')

			# If the list length is 3,  it corresponds to one of measured masses
			if len(out) == 3 and out[0] == "MassReading":
				new_row = [time.time(), float(out[1]), float(out[2])]  # The row is : time, mass number, mass pressure
				mass_read = numpy.vstack([mass_read, new_row])  # Adding measured value to array
				if float(out[1]) == mass_selected[-1]:  # When last mass value of scan is read , restart scan
					self.rga_id03.write("ScanResume 1\n")

		# Stop scan
		self.rga_id03.write("ScanStop\n")
		print(self.rga_id03.read("never", 1))  # Collect all garbage output
		print("Mass read stop...")
		self.status[3] = 0
		self.scan = True

	# Stop scan
	def rga_peakscan_stop(self):
		if self.scan:
			self.scan = False
		else:
			print("Rga is not scanning, nothing to stop")

	# Read one mass
	def rga_onemass(self, one_mass):

		find_mass = numpy.nonzero(mass_read == one_mass)
		mass_found = mass_read[find_mass[0], :]
		out = [int(mass_found[-1, 0]), int(mass_found[-1, 1]), mass_found[-1, 2]]
		return out

	def rga_status(self):

		status_str = []

		status_str.append([["not connected"], ["connected"], ["RGA connection : "]])
		status_str.append([["not controlled"], ["controlled"], ["RGA control : "]])
		status_str.append([["off"], ["on"], ["Filament status :"]])
		status_str.append([["idle"], ["running"], ["Scan status: "]])

		for i in range(4):
			print("".join(map(str, (status_str[i][2]))) + "".join(map(str, (status_str[i][self.status[i]]))))

if __name__ == "__main__":
	rga_eh1 = RGA("rga-id03-eh1", 10014)
	rga_eh1.rga_release()