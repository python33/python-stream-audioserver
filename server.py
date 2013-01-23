from __future__ import with_statement
import audioread
import os
from SocketServer import ThreadingMixIn, UDPServer, BaseRequestHandler

class RequestHandler( BaseRequestHandler ):
    
    def __init__(self, request, client_address, server):
        BaseRequestHandler.__init__(self, request, client_address, server)
    
    def _open_file(self, filename):
        filename = os.path.abspath(os.path.expanduser(filename))
        try:
            return audioread.audio_open(filename)
        except Exception, e:
            print "File doesnt exist: %s" % filename
            return False
    
    def handle(self):
        f = self._open_file("/Users/Jorgenkg/Desktop/sheep.mp3")
        if f:
            print 'Input file: %i channels at %i Hz; %.1f seconds.' % (f.channels, f.samplerate, f.duration)
            f.read_data()
            f.close()
        recieved_data, connection = self.request
        connection.sendto(recieved_data.upper(), self.client_address)
    
class StreamServer(UDPServer):
    def __init__(self, server_address=('', 8080)):
        UDPServer.__init__(self,
                        server_address,
                        RequestHandler
                    )

class ThreadedStreamServer(ThreadingMixIn, StreamServer):
    pass
    

if __name__ == '__main__':
    server = ThreadedStreamServer()
    try:
        print "Server is running."
        server.serve_forever()
    except KeyboardInterrupt:
        print "\nServer is shuting down. \nPlease wait for the called requests to terminate."
        server.server_close()
