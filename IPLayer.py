import socket
from struct import *
from IPPacket import IPPacket

class IPLayer:
    rc = None
    ss = None

    src = None

    def __init__(self):
        self.rc = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
        self.ss = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
        self.ss.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, True)
        self.src = IPLayer.get_ip_address()

    def send(self, dst, data):
        pkt = IPPacket()
        pkt.SRC = socket.inet_aton(self.src)
        pkt.Dest = socket.inet_aton(dst)
        pkt.Data = data

        self.ss.sendto(pkt.toHexString(), (dst, 0))

    def recv(self):
        raw_data, addr = self.rc.recvfrom(65565)
        ippkt = IPPacket()
        ippkt.fromData(raw_data)
        return ippkt

    @staticmethod
    def get_ip_address():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]