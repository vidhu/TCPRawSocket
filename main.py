import atexit

from IPLayer import IPLayer
from TCPSocket import TCPSocket


s = None
def main():
    ipLayer = IPLayer()
    s = TCPSocket(ipLayer)
    #s.connect('192.168.0.21', 8080)
    s.connect('216.97.236.245', 80)
    #s.connect('66.147.244.191', 80)

    #s.send("GET /big.html HTTP/1.0\r\nHost: 192.168.0.21:8080\r\nConnection: keep-alive\r\nAccept: text/html\r\n\r\n")
    s.send("GET /classes/cs4700fa16/2MB.log HTTP/1.0\r\nHost: david.choffnes.com\r\nAccept: text/html\r\n\r\n")
    #s.send("GET / HTTP/1.0\r\nHost: motherfuckingwebsite.com\r\nAccept: text/html\r\n\r\n")


    #data = s.recv(1)
    while(not s.closeInitiated):
        pass

    with open("2MB.log", "w") as file:
        file.write(s.RecvData.split('\r\n\r\n')[1])

    print "done!"


    #s.close()


def exit_handler():
    if (open):
        s.close()

#atexit.register(exit_handler)
main()


