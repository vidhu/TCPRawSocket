import atexit
import sys
import socket
from urlparse import urlparse
from IPLayer import IPLayer
from TCPSocket import TCPSocket


s = None
def main():
    #Get url from cmd line parameters
    url = sys.argv[1:][0]

    #Get variables
    url = urlparse(url)
    host = url[1]
    path = url[2]
    ip = getIpAddress(host)

    if(path[-1] == '/'):
        path += "index.html"

    #Set File name
    filename = path.split('/')[-1]

    #Create TCP socket and send request
    ipLayer = IPLayer()
    s = TCPSocket(ipLayer)
    s.connect(ip, 80)
    s.send("GET {} HTTP/1.1\r\nHost: {}\r\nAccept: text/html\r\n\r\n".format(path, host))

    #Wait for socket to be closed
    while(not s.closeInitiated):
        pass

    #Write File to disk
    with open(filename, "w") as file:
        file.write(s.RecvData.split('\r\n\r\n')[1])



def getIpAddress(url):
    return socket.gethostbyname(url)

main()


