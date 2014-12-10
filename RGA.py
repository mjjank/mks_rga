import sys
import telnetlib
import time
import numpy
# Connecting to RGA - RGA(HOST,PORT)


class RGA:

	scan = True  # This is used for stop, peak scan - if set to False
	status = [0 for col in range(4)]  # Status of the device
	showReadout = True  # This one suppresses or not text output from RGA

	# Class constructor
	def __init__(self, host, port):

		print("Starting connection with RGA: ")
		self.telCon = telnetlib.Telnet(host, port)
		out = self.rga_readout(0, True)
		if out.find("MKSRGA  Single") > -1:
			self.status[0] = 1

		print("List of available sensors: ")
		self.telCon.write("Sensors\n")
		out = self.rga_readout(0, True)

		out = out.replace("\r", "")  # Removing \r, \n form the output
		out = out.replace("\n", "")
		out = out.split(' ')
		out = filter(None, out)  # Removing empty fields

		print("Status of sensors with RGA: ")
		self.telCon.write("SensorState\n")
		self.rga_readout(0, True)

		print("Selecting sensor: ")
		sensor = "Select " + out[7] + "\n"
		self.telCon.write(sensor)
		self.rga_readout(0, True)


		print("Taking control over the sensor: ")
		self.telCon.write("Control \"RGA python server\" \"1.0\" \n")
		out = self.rga_readout(0, True)
		if out.find("Control OK") > -1:
			self.status[1] = 1



	# Read output
	def rga_readout(self, timeout, show):

		if self.showReadout is True and show is True and timeout == 0:
			out = self.telCon.read_until("\r\r")
			print(out)
		elif self.showReadout is True and show is True and timeout > 0:
			out = self.telCon.read_until("\r\r", timeout)
			print(out)
		elif self.showReadout is False and timeout == 0:
			out = self.telCon.read_until("\r\r")
		elif self.showReadout is False and timeout > 0:
			out = self.telCon.read_until("\r\r", timeout)
		else:
			out = "Readout error !!!!"
			print(out)
		return out

	# Release
	def rga_release(self):

		print("Release of the sensor: ")

		self.telCon.write("Release\n")
		self.rga_readout(1, True)
		self.status[1] = 0
		self.status[0] = 0

	# Filament control
	def rga_filament(self, state):

		if state == "On":
			self.telCon.write("FilamentControl On\n")
			time.sleep(5)
			self.rga_readout(0, True)  # Little bit robust but works
			self.rga_readout(0, True)
			self.rga_readout(0, True)
			self.rga_readout(0, True)
			self.status[2] = 1
		elif state == "Off":
			self.telCon.write("FilamentControl Off\n")
			time.sleep(5)
			self.rga_readout(0, True)  # Little bit robust but works
			self.rga_readout(0, True)
			self.rga_readout(0, True)
			self.rga_readout(0, True)
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
		self.telCon.write("AddPeakJump Peak1 PeakCenter 2 0 0 0\n")
		self.rga_readout(0, True)

		# Adding masses to scan
		for i in range(len(mass_selected)):

				self.telCon.write("MeasurementAddMass " + str(mass_selected[i]) + "\n")  # Here we again convert number to string - just for training
				self.rga_readout(0, True)
		time.sleep(1)
		# Adding scan to scan list
		self.telCon.write("ScanAdd Peak1\n")
		self.rga_readout(0, True)

		# Starting scan
		self.telCon.write("ScanStart 1\n")

		self.status[3] = 1

		while self.scan:

			# Processing output string
			#out = self.telCon.read_until("\r\r", 1)
			out = self.rga_readout(1, True)
			out = out.split(' ')
			out = filter(None, out)

			# If the list length is 3,  it corresponds to one of measured masses
			if len(out) == 3 and out[0] == "MassReading":
				new_row = [time.time(), float(out[1]), float(out[2])]  # The row is : time, mass number, mass pressure
				mass_read = numpy.vstack([mass_read, new_row])  # Adding measured value to array
				if float(out[1]) == mass_selected[-1]:  # When last mass value of scan is read , restart scan
					self.telCon.write("ScanResume 1\n")

		# Stop scan
		self.telCon.write("ScanStop\n")
		print(self.telCon.read_until("never", 1))  # Collect all garbage output
		print("Mass read stop...")
		self.status[3] = 0
		self.scan = True

	# Stop scan
	def rga_peakscan_stop(self):
		if self.scan == True:
			self.scan = False

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



