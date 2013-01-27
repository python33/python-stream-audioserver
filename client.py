import socket
import select

DEBUG = True
CONNECTION = ('', 8080)

class AudioSocket( socket.socket ):
    
    def __init__(self, family=socket.AF_INET, type=socket.SOCK_STREAM):
        socket.socket.__init__(self, family, type)
        try:
            self.connect( CONNECTION )
            if DEBUG: print "* added to server stream"
        except Exception:
            print "ERROR: not able to connect to server"
    
    def _wait_response(self, block_size = 1024):
        ready = select.select([self], [], [], 30*60)
        if ready[0]:
            return self.recv(block_size)
    
    def _do_action(self, msg):
        if 'stop' == msg.lower():
            if DEBUG: print "* Server signaled shutdown"
            self.run = False
            self.close()
        elif 'playing' == msg.lower(): 
            self.play()
    
    def play(self): pass
    
    def start(self):
        self.run = True
        
        try:
            while self.run:
                self._do_action( self._wait_response() )
        except KeyboardInterrupt:
            if DEBUG: print "* Disconnected from host"
            self.sendall("bye")
            self.close()
        
a = AudioSocket()
a.start()