from __future__ import with_statement
import audioread
import pyaudio
import os
from SocketServer import ThreadingMixIn, UDPServer, BaseRequestHandler


class RequestHandler( BaseRequestHandler ):
    
    def __init__(self, request, client_address, server):
        BaseRequestHandler.__init__(self, request, client_address, server)
        
    
    def handle(self):
        recieved_data, connection = self.request
        self._audiorender = pyaudio.PyAudio()
        
        f = audioread.audio_open(os.path.join(os.path.dirname(__file__),"test.mp3"))
        
        stream = self._audiorender.open(
                                        format=pyaudio.paInt16,
                                        channels=f.channels,
                                        rate=f.samplerate,
                                        output=True
                                    )
        for buff in f:
            stream.write(buff)
        f.close()
        stream.stop_stream()
        stream.close()
        
        self._audiorender.terminate()
        
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
