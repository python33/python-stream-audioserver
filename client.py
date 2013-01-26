import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setblocking(1)

sock.sendto("test\n", ('', 8080))

sock.recv(1024) # equals a wait
print "Sound is played."