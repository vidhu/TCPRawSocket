import socket
from struct import *

class IPPacket:
    #Packet Fields
    Version = 4
    Hlen = 5
    Service = 0
    Len = 0
    Identification = 54321
    Flags = 0
    FragmentOfset = 0
    TTL = 255
    ULP = 6
    CheckSum = 0
    SRC = socket.inet_aton("192.168.0.248")
    Dest = socket.inet_aton("192.168.0.21")
    #SRC = socket.inet_aton("192.168.0.1")
    #Dest = socket.inet_aton("192.168.1.1")
    Opt = None
    Data = None

    def __init__(self):
        pass

    def toHexString(self):
        ip_ver_hlen = (self.Version << 4) + self.Hlen
        return pack('!BBHHHBBH4s4s',
             ip_ver_hlen,
             self.Service,
             self.Len,
             self.Identification,
             self.FragmentOfset,
             self.TTL,
             self.ULP,
             self.CheckSum,
             self.SRC,
             self.Dest) + self.Data

    def fromData(self, data):
        ver_hlen, service, dlen, id, frag_offset, ttl, proto, chksum, src, dst = unpack('!BBHHHBBH4s4s',
                                                                                               data[:20])
        self.Version = (ord(data[0]) >> 4)
        self.Hlen = (ord(data[0]) & 15) * 4
        self.Service = service
        self.Len = dlen
        self.Identification = id
        self.Flags = frag_offset
        self.FragmentOfset = frag_offset
        self.TTL = ttl
        self.ULP = proto
        self.CheckSum = chksum
        self.SRC = src
        self.Dest = dst
        self.Data = data[20:]

    def __str__(self):
        #s = ":".join("{:02x}".format(ord(c)) for c in self.Data)
        s = "\n"
        s += "IPv4 Packet:\n"
        s += "\t Version: {}, Header Length: {}, TTL: {}\n".format(self.Version, self.Hlen, self.TTL)
        s += "\t Protocol: {}, Source: {}, Destination: {}\n".format(self.ULP, socket.inet_ntoa(self.SRC), socket.inet_ntoa(self.Dest))
        return s