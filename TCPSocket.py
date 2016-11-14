import sys
import time
import thread
import threading
from IPLayer import IPLayer
from TCPPacket import TCPPacket

class TCPSocket:
    _localport = 1235
    _iplayer = None
    _socketOpen = False
    _cwnd = 1
    closeInitiated = False
    IP = None   # IP to connect to
    Port = None # Port to connect to

    NextSEQNum = 0
    NextACKNum = 0

    SendData = ""
    RecvData = ""

    UnAckedPkts = []
    RecvPkts = []

    LargestAck = 0

    def __init__(self, iplayer):
        self._iplayer = iplayer

        recv_thread = threading.Thread(target=self._recvthread)
        recv_thread.daemon = True
        recv_thread.start()

        send_thread = threading.Thread(target=self._sendthread)
        send_thread.daemon = True
        send_thread.start()


    def send(self, data):
        self.SendData += data

    def recv(self, length):
        returnData = self.RecvData[:length]
        self.RecvData = self.RecvData[length:]
        return returnData

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

    def _sendthread(self):
        mss = 256

        while(True):
            if(len(self.UnAckedPkts) > 0):
                curtime = time.time()
                earliestTime, earliestPkt = self.UnAckedPkts[0]
                if(curtime - earliestTime > 60):
                    #Timeout occured here

                    #reset cwnd
                    self._cwnd = 1

                    #remove the timesout packet so it can be resent
                    self.UnAckedPkts = self.UnAckedPkts[1:]

                    #retransmit packet
                    self._iplayer.send(self.IP, earliestPkt.toHexString())

                    # add (timestamp, pkt) to unacked packet list
                    self.UnAckedPkts.append((time.time(), pkt))
                continue

            #Send Packet if Data exist
            if(len(self.SendData) > 0 and len(self.UnAckedPkts) < self._cwnd):
                pkt = self.makeTCPPacket()
                pkt.fACK = 1
                pkt.DATA = self.SendData[:mss]

                self.SendData = self.SendData[mss:]

                self._send(pkt)

                #add (timestamp, pkt) to unacked packet list
                self.UnAckedPkts.append((time.time(), pkt))






    def _recvthread(self):
        while True:
            #Get TCP Packet
            ippkt = self._iplayer.recv()
            tcppkt = TCPPacket()
            tcppkt.fromData(ippkt.Data)

            if(tcppkt.DST == self._localport):
                #print tcppkt
                #if packet SEQ is not expected? (out of order) skip it
                #ignore syn flagged packetrs since its the fist packet
                #so there is no way of knowing the expected seq number
                if(tcppkt.fSYN == 0 and tcppkt.SEQ != (self.NextACKNum)):
                    print "out of order packet"
                    print "SEQ: {}\tEXP: {}".format(tcppkt.SEQ, self.NextACKNum)
                    print "Acking: {}".format(self.NextACKNum)
                    #Ack last packet
                    self._sendAck()
                    continue



                # Don't ACK the ACK packets received. ACK all others
                if(not(tcppkt.fACK == 1 and len(tcppkt.DATA) == 0 and tcppkt.fFIN == 0 and tcppkt.fSYN != 1)):
                    if (len(tcppkt.DATA) == 0):
                        self.NextACKNum = tcppkt.SEQ + 1
                    else:
                        self.NextACKNum = tcppkt.SEQ + len(tcppkt.DATA)

                    self._sendAck()
                    self.RecvData += tcppkt.DATA
                    #sys.stdout.write(tcppkt.DATA)

                #When you receive an ACK
                if(tcppkt.fACK == 1):
                    self.LargestAck = tcppkt.ACK
                    self._cwnd += 1

                #Close connection if FIN packet is received
                if(tcppkt.fFIN == 1):
                    if((not self.closeInitiated)):
                        self.close()

                #If RST PKT, close
                if(tcppkt.fRST == 1):
                    print "Received RST flagged packet"
                    self._socketOpen = False
                    return

                self.RecvPkts.append(tcppkt)

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
            #If a packet exists in the buffer
            if(len(self.RecvPkts) > 0):
                #Remove the packet
                tcppkt = self.RecvPkts[0]
                self.RecvPkts = self.RecvPkts[1:]
                #And check if its a SYN-ACK
                if(tcppkt.fSYN == 1 and tcppkt.fACK == 1):
                    #Break if it is
                    break

        time.sleep(1)
        self._socketOpen = True

        print "================================="
        print "Connected!!"
        print "================================="

    def close(self):
        print "================================="
        print "Closing Connection"
        print "================================="
        if (not self._socketOpen):
            return

        self.closeInitiated = True

        #Send Fin ACK
        fin = self.makeTCPPacket()
        fin.fFIN = 1
        fin.fACK = 1
        self._send(fin)

        # Wait for FIN ACK
        while (True):
            # If a packet exists in the buffer
            if (len(self.RecvPkts) > 0):
                # Remove the packet
                tcppkt = self.RecvPkts[0]
                self.RecvPkts = self.RecvPkts[1:]
                # And check if its a FIN-ACK
                if(tcppkt.fFIN == 1):
                    break

        self._socketOpen = False

    def makeTCPPacket(self):
        pkt = TCPPacket()
        pkt.setIP(IPLayer.get_ip_address(), self.IP)
        pkt.SRC = self._localport
        pkt.DST = self.Port
        return pkt
