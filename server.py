# Server class
import socket
import sys
import time
import threading
from RGA import *


class RgaServer:

    rga_eh1 = 0  # Object for RGA class
    status = [0 for col in range(5)]  # Status of the server
    reply2 = ""  # Variable which consists telnet output to a connected client

    # Class constructor
    def __init__(self):
        pass

    # Starts server on local computer using given, fixed port
    def server_start(self):

        host = ""
        port = 8888

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # This is needed in order to re-use port after restarting server
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

        # Keeps server alive for sending and receiving commands
        # On the base: http://www.binarytides.com/python-socket-programming-tutorial/
        while True:
                # Wait to accept a connection - blocking call
                conn, addr = s.accept()
                print("Connected with " + addr[0] + ':' + str(addr[1]))

                reply = "Connection established\r\n"

                data = conn.recv(1024)

                if not data:
                    break
                conn.sendall(reply)
                self.status[0] = 1
                break
        # Continuous sending and receiving data
        while True:

            data = conn.recv(1024)
            data = data.replace("\r\n", "")  # Removing not necessary part of the received string
            self.server_send(data)
            if data.find("exit") > -1:  # "exit" causes shut down of the socket
                self.status[0] = 0
                break
            conn.sendall(self.reply2)

        conn.close()
        s.close()
        print("Server shut down")

    def server_stop(self):
        # Optional for future
        pass

    # Status of the server - need to be developed in the future
    def server_status(self):

        if self.status[0] == 0:
            print("Server not running\n")
        elif self.status[0] == 1:
            print("Server is running\n")
        elif self.status[0] == 0:
            print("RGA is not running\n")
        elif self.status[1] == 1:
            print("RGA is running\n")
    # Commands analysis
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
            self.reply2 = ""
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

if __name__ == "__main__":

    # Server address is rga-id03-eh1 10014

    # Server object
    s = RgaServer()

    # Starting server
    s.server_send("server start")