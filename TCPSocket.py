import socket
from IPLayer import IPLayer
from TCPPacket import TCPPacket

class TCPSocket:
    _iplayer = None
    IP = None   # IP to connect to
    Port = None # Port to connect to

    NextSEQNum = 0
    NextACKNum = 0

    def __init__(self, iplayer):
        self._iplayer = iplayer

    def send(self, data):
        pkt = self.makeTCPPacket()
        pkt.fACK = 1
        pkt.DATA = data
        self._send(pkt)


        #Collect Data Here
        data = ""
        while("Hello" not in data):
            pkt = self.recv()
            data += pkt.DATA


        print data


    def _send(self, pkt):
        pkt.SEQ = self.NextSEQNum

        if (pkt.fACK == 1):
            pkt.ACK = self.NextACKNum

        if (pkt.fSYN == 1 or pkt.fFIN == 1):
            self.NextSEQNum = self.NextSEQNum + 1
        elif (pkt.fACK == 1 and len(pkt.DATA) == 0):
            self.NextSEQNum = self.NextSEQNum
        elif (len(pkt.DATA) != 0):
            self.NextSEQNum = self.NextSEQNum + len(pkt.DATA)

        #print pkt
        self._iplayer.send(self.IP, pkt.toHexString())

    def _sendAck(self):
        ack = self.makeTCPPacket()
        ack.fACK = 1
        self._send(ack)

    def recv(self):
        while True:
            ippkt = self._iplayer.recv()
            tcppkt = TCPPacket()
            tcppkt.fromData(ippkt.Data)

            if(tcppkt.DST == 1234):
                if(len(tcppkt.DATA) == 0):
                    self.NextACKNum = tcppkt.SEQ + 1
                else:
                    self.NextACKNum = tcppkt.SEQ + len(tcppkt.DATA)

                # Don't ACK the ACK packets received. ACK all others
                if(not(tcppkt.fACK == 1 and len(tcppkt.DATA) == 0 and tcppkt.fFIN != 0)):
                    self._sendAck()

                #print tcppkt
                return tcppkt

    def connect(self, ip, port):
        self.IP = ip
        self.Port = port

        print "================================="
        print "Opening Connection"
        print "================================="

        #Send SYN
        syn = self.makeTCPPacket()
        syn.fSYN = 1
        self._send(syn)

        #Wait for SYN-ACK
        while(True):
            tcppkt = self.recv()
            if(tcppkt.fSYN == 1 and tcppkt.fACK == 1):
                break



        print "================================="
        print "Connected!!"
        print "================================="

    def close(self):
        print "================================="
        print "Closing Connection"
        print "================================="

        #Send Fin ACK
        fin = self.makeTCPPacket()
        fin.fFIN = 1
        fin.fACK = 1
        self._send(fin)

        # Wait for FIN ACK
        while (True):
            tcppkt = self.recv()
            if(tcppkt.fFIN == 1):
                break



    def makeTCPPacket(self):
        pkt = TCPPacket()
        pkt.setIP(IPLayer.get_ip_address(), self.IP)
        pkt.SRC = 1234
        pkt.DST = self.Port
        return pkt
