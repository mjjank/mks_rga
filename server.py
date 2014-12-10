# Server class
import socket
import sys
import time
import threading
from RGA import *

class RgaServer:

    rga_eh1 = 0
    status = [0 for col in range(5)]
    reply2 = ""

    def __init__(self):
        pass

    def server_start(self):

        host = ""
        port = 8888
        #global data


        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # This is needed in order to re-use port after program stop
        except socket.error as msg:
            print("Socket creation failed. Error code: " + str(msg[0]) + " Error message: " + msg[1])
            sys.exit()
        print("Socked Created")

        try:
            s.bind((host, port))
        except socket.error as msg:
            print("Bind failed. Error Code : " + str(msg[0]) + " Message " + msg[1])
            sys.exit()

        print("Socket bind complete")

        s.listen(10)
        print("Socket now listening")

        # now keep talking with the client
        while True:
                # wait to accept a connection - blocking call
                conn, addr = s.accept()
                print("Connected with " + addr[0] + ':' + str(addr[1]))

                reply = "Connection established\r\n"

                data = conn.recv(1024)

                if not data:
                    break
                conn.sendall(reply)
                self.status[0] = 1
                reply=""
                break

        while True:

            data = conn.recv(1024)
            data=data.replace("\r\n", "")
            self.server_send(data)
            if data.find("exit") > -1:
                self.status[0] = 0
                break
            conn.sendall(self.reply2)

        conn.close()
        s.close()
        print("Server exit")

    def server_stop(self):
        # Something to add here
        pass

    def server_status(self):

        if self.status[0] == 0:
            print("Server not running\n")
        elif self.status[0] == 1:
            print("Server is running\n")
        elif self.status[0] == 0:
            print("RGA is not running\n")
        elif self.status[1] == 1:
            print("RGA is running\n")

    def server_send(self, command):
        # Rga commands
        if command.find("rga start") > -1:
            com = command.split(" ")
            self.rga_eh1 = RGA(com[2], com[3])
        elif command == "rga release":
            self.rga_eh1.rga_release()
        elif command == "rga status":
            self.rga_eh1.rga_status()
        elif command == "rga filament on":
            self.rga_eh1.rga_filament("On")
        elif command == "rga filament off":
            self.rga_eh1.rga_filament("Off")
        elif command.find("rga peakscan start") > -1:
            command = command.replace("rga peakscan start ", "")
            command = command.split(" ")
            t2 = threading.Thread(target=self.rga_eh1.rga_peakscan, args=(command,))
            t2.daemon = True
            t2.start()

        elif command == "rga peakscan stop":
            self.rga_eh1.rga_peakscan_stop()
        elif command.find("mass ") > -1:
            command = command.replace("mass ", "")
            command = self.rga_eh1.rga_onemass(int(command))
            self.reply2 = str(command) + "\r\n"

        # Server commands
        elif command == "server start":
            t1 = threading.Thread(target=self.server_start, args=())
            t1.daemon = False
            t1.start()
        elif command == "test":
             print("Test works")

