from __future__ import with_statement
import audioread
import pyaudio
import os
from SocketServer import ThreadingMixIn, UDPServer, BaseRequestHandler


class RequestHandler( BaseRequestHandler ):

    def __init__(self, request, client_address, server):
        BaseRequestHandler.__init__(self, request, client_address, server)
        
    def _open_file(self, filename):
        self._file = audioread.audio_open( filename )
    
    def handle(self):
        received_data, connection = self.request
        
        self._open_file( os.path.join(os.path.dirname(__file__),"test.mp3") )
        self._audiorender = pyaudio.PyAudio()
        
        self.stream = self._audiorender.open(
                                        format=pyaudio.paInt16,
                                        channels=self._file.channels,
                                        rate=self._file.samplerate,
                                        output=True
                                    )
        for buff in self._file:
            self.stream.write(buff)
        
        
        self._file.close()
        self.stream.stop_stream()
        self.stream.close()
        self._audiorender.terminate()
        
        connection.sendto("1", self.client_address) # signal that we are done
    
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