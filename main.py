import atexit
import socket
import struct
import sys
from IPLayer import IPLayer
from IPPacket import IPPacket
from TCPPacket import TCPPacket
from TCPSocket import TCPSocket

def sendSetup():
    ss = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
    ss.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, True)

    ippkt = IPPacket()
    tcppkt = TCPPacket()
    tcppkt.setIP("192.168.0.248", "192.168.0.21")

    pkt = ippkt.toHexString() + tcppkt.toHexString()

    ss.sendto(pkt, ("192.168.0.21", 0))


def rcvSetup():
    rs = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
    while True:
        raw_data, addr = rs.recvfrom(65565)
        #print raw_data
        ippkt = IPPacket()
        ippkt.fromData(raw_data)
        print ippkt
        tcppkt = TCPPacket()
        tcppkt.fromData(ippkt.Data)
        print tcppkt
        print tcppkt.DATA
        #print raw_data

s = None
open = False
def main():
    ipLayer = IPLayer()
    s = TCPSocket(ipLayer)
    s.connect('192.168.0.21', 8080)
    open = True
    s.send("GET / HTTP/1.1\nHost: 192.168.0.21:8080\nConnection: keep-alive\nAccept: text/html\n\n")

    data = s.recv(1)
    while('\r\n\r\n' not in data):
        data += s.recv(1)
    print data

    if(open):
        s.close()


def exit_handler():
    if (open):
        s.close()

atexit.register(exit_handler)
main()
#sendSetup()