import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock.sendto("test\n", ('', 8080))
print "Received: {}".format(sock.recv(1024))