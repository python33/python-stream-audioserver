import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock.sendto("test\n", ('', 8080)) # just to instatiate a handler on the server