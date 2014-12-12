import telnetlib

__author__ = 'Maciej Jankowski'

class RgaTelnet:

    def __init__(self, host, port):
        host = host.encode('ascii')
        self.tc = telnetlib.Telnet(host, port)

    def read(self, msg_end, timeout):
        out = self.tc.read_until(msg_end.encode('ascii'), timeout).decode('ascii')
        return out

    def write(self, command):
        command = command.encode('ascii')
        self.tc.write(command)

if __name__ == "__main__":

    rga_id03 = RgaTelnet("rga-id03-eh1", 10014)
    print(rga_id03.read("\r\r", 1))
    rga_id03.write("Sensors\n")
    print(rga_id03.read("\r\r", 1))