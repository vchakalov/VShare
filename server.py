import socket

localIp = '127.0.0.1'
port = 20001

bufferSize = 1024
address = (localIp, port)
server = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
server.bind(address)

    



