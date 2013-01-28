import audioread
import os
from SocketServer import ThreadingMixIn, BaseRequestHandler,\
    TCPServer
import threading
import select


DEBUG = True

class RequestHandler( BaseRequestHandler ):

    def __init__(self, request, client_address, server):
        BaseRequestHandler.__init__(self, request, client_address, server)
    
    def _send(self, msg):
        self.request.sendall(msg)
            
    def _do_action(self, msg):
        if 'bye' == msg.lower():
            if DEBUG: print "* disconnecting sink: %s:%d" % self.request.getsockname()
            self.run = False
            self.server.remove_audiosink( self.request )
        else: 
            return False
        return True
    
    def _wait_response(self, block_size = 1024):
        ready = select.select([self.request], [], [], 30*60)
        if ready[0]:
            return self.recv(block_size)
    
    def handle(self):
        self.run = True
        self.server.add_audiosink( self.request )
        
        try:
            while self.run:
                command = self._wait_response()
                if self._do_action( command ):
                    self._send("ok")
                else:
                    print "ERROR: unknown command: %s" % command
                    self._do_action("bye")
        except Exception:
            self._do_action("bye")
    
class StreamServer(TCPServer):
    
    def __init__(self, server_address=('', 8080)):
        TCPServer.__init__(self,
                        server_address,
                        RequestHandler
                    )
        self.sinks = [ ]
        self.is_playing = False
        self.lock = threading.Lock()
        
    def server_close(self):
        for sink in self.sinks:
            sink.sendall("stop")
        
        TCPServer.server_close(self)
    
    def add_audiosink(self, sink):
        self.lock.acquire()
        
        if DEBUG: print "* Add sink: %s:%d" % sink.getsockname()
        self.sinks.append(sink)
        self.lock.release()
        
        self.play()
        
    def remove_audiosink(self, sink):
        self.lock.acquire()
        for index, element in enumerate( self.sinks ):
            if sink == element: del self.sinks[index]
        if DEBUG: print "* Remove sink: %s:%d" % sink.getsockname()
        self.lock.release()
    
    def send_all(self, data):
        for sink in self.sinks:
            sink.sendall(data)
    
    def _stream_audio(self):
        self._file = audioread.audio_open( os.path.join(os.path.dirname(__file__), "test.mp3" ))
        print "playing,%d,%d" % (self._file.channels, self._file.samplerate)
        self.send_all("playing,%d,%d" % (self._file.channels, self._file.samplerate))

        for buff in self._file:
            for sink in self.sinks:
                sink.sendall(buff)
        
        self._file.close()
        
        self.lock.acquire()
        self.is_playing = False
        self.lock.release()
    
    def play(self):
        self.lock.acquire()
        if not self.is_playing:
            self.is_playing = True
            if DEBUG: print "* Streaming to %d sinks." % len(self.sinks)
            self.lock.release()
            
            self._stream_audio()

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