from SocketServer import ThreadingMixIn, UDPServer

class RequestHandler( StreamRequestHandler ):
    def handle(self):
        self.data = self.rfile.readline() # read data
        self.wfile.write(self.data.upper()) # send data back through the connection
    
class StreamServer( UDPServer ):
    def __init__(self, server_address = ('', 8080) ):
        UDPServer.__init__(self, 
                        server_address, 
                        RequestHandler
                    )

class ThreadedStreamServer(ThreadingMixIn, PipeServer):
    pass
    

if __name__ == '__main__':
    server = ThreadedStreamServer()
    try:
        print "Server is running."
        server.serve_forever()
    except KeyboardInterrupt:
        print "\nServer is shuting down. \nPlease wait for the called requests to terminate."
        server.server_close()
