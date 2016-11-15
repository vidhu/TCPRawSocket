import socket
from struct import *

class TCPPacket:
    _srcip = None
    _dstip = None

    SRC = 1234
    DST = 8080
    SEQ = 1
    ACK = 0
    LEN = 5
    #RES = None

    #Flags
    fURG = 0
    fACK = 0
    fPSH = 0
    fRST = 0
    fSYN = 0
    fFIN = 0


    WND = socket.htons(5840)
    CHK = 0
    URG = 0
    OPT = ''
    DATA = ""

    def __int__(self):
        pass

    def setData(self, data):
        self.DATA = data

    def setIP(self, src, dest):
        self._srcip = src
        self._dstip = dest

    def toHexString(self):
        tcp_flags = self.fFIN + (self.fSYN << 1) + (self.fRST << 2) + (self.fPSH << 3) + (self.fACK << 4) + (self.fURG << 5)

        header = pack('!HHLLBBHHH',
                      self.SRC,
                      self.DST,
                      self.SEQ,
                      self.ACK,
                      (self.LEN << 4) + 0,
                      tcp_flags,
                      self.WND,
                      self.CHK,
                      self.URG)

        #Calculate Data length
        data_len = 0
        if(self.DATA != None):
            data_len = len(self.DATA)

        #Create Pseudo TCP Packet
        psh = pack('!4s4sBBH',
                    socket.inet_aton(self._srcip),
                    socket.inet_aton(self._dstip), 0, socket.IPPROTO_TCP, len(header) + data_len)
        psh = psh + header + (self.DATA if self.DATA != None else "")


        checksum = self.checkSum(psh)

        return pack('!HHLLBBH',
                        self.SRC,
                        self.DST,
                        self.SEQ,
                        self.ACK,
                        (self.LEN << 4) + 0,
                        tcp_flags,
                        self.WND) + pack('H', checksum) + pack('!H', self.URG) \
               + (self.DATA if self.DATA != None else "")


    def checkSum(self, data):
        s = 0

        # sum of 1 complements. Add byte after byte
        for i in range(0, len(data), 2):
            if(i == len(data)-1):
                w = ord(data[i]) + (0x00 << 8)
            else:
                w = ord(data[i]) + (ord(data[i + 1]) << 8)
            s = s + w

        s = (s >> 16) + (s & 0xffff)
        s = s + (s >> 16)

        # get first 4 least significant bytes
        s = ~s & 0xffff

        return s

    def validChecksum(self):
        #Construct TCP Header
        tcp_flags = self.fFIN + (self.fSYN << 1) + (self.fRST << 2) + (self.fPSH << 3) + (self.fACK << 4) + (
        self.fURG << 5)
        header = pack('!HHLLBBHHH',
                      self.SRC,
                      self.DST,
                      self.SEQ,
                      self.ACK,
                      (self.LEN << 4) + 0,
                      tcp_flags,
                      self.WND,
                      0,
                      self.URG)
        header += self.OPT

        # Calculate Data length
        data_len = 0
        if (self.DATA != None):
            data_len = len(self.DATA)

        # Create Pseudo TCP Packet
        psh = pack('!4s4sBBH',
                   socket.inet_aton(self._srcip),
                   socket.inet_aton(self._dstip), 0, socket.IPPROTO_TCP, (len(header)) + data_len)
        psh = psh + header + (self.DATA if self.DATA != None else "")

        checksum = self.checkSum(psh)

        return pack('<H', checksum) == pack('>H', self.CHK)

    def fromData(self, data):
        src, dst, seq, ack, hlen, flags, wnd, chksum, urg = unpack("!HHLLBBHHH", data[:20])
        self.SRC = src
        self.DST = dst
        self.SEQ = seq
        self.ACK = ack
        self.LEN = (hlen >> 4)
        self.WND = wnd
        self.CHK = chksum
        self.URG = urg
        self.OPT = data[20:hlen >> 2]

        (self.fURG, self.fACK, self.fPSH, self.fRST, self.fSYN, self.fFIN) = TCPPacket.getFlagsFromByte(flags)

        self.DATA = data[self.LEN*4:]

    def __str__(self):
        s = ""
        s += "TCP Segment"
        s += "\tSource Port: {}, Destination Port: {}\n".format(self.SRC, self.DST)
        s += "\tSequence: {}, Acknowledgement: {}\n".format(self.SEQ, self.ACK)
        s += "\tFlags\n"
        s += "\t\tURG: {}, ACK: {}, PSH: {}\n".format(self.fURG, self.fACK, self.fPSH)
        s += "\t\tRST: {}, SYN: {}, FIN: {}\n".format(self.fRST, self.fSYN, self.fFIN)
        s += "\tHeader Length: {}, Window Size: {}\n".format(self.LEN, self.WND)

        return s

    @staticmethod
    def getFlagsFromByte(data):
        flags = [0,0,0,0,0,0]

        flags[0] = (data >> 5) & 1
        flags[1] = data >> 4 & 1
        flags[2] = data >> 3 & 1
        flags[3] = data >> 2 & 1
        flags[4] = data >> 1 & 1
        flags[5] = data & 1

        return (flags[0], flags[1], flags[2], flags[3], flags[4], flags[5])
