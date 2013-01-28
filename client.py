import socket, select, threading
import pyaudio
from Queue import Queue

DEBUG = True
CONNECTION = ('', 8080)

STOP = 'stop'
PLAYING = 'playing'
BYE = 'bye'

class Player( object ):
    
    def __init__(self):
        self.buffer = Queue()
        self.lock = threading.Lock()
        self.play_thread = False
        
    def _play(self, lock, channels, rate, audio_format):
        if DEBUG: print "* receiving audio stream"
        self._audiorender = pyaudio.PyAudio()
        self.stream = self._audiorender.open(
                                        format=audio_format,
                                        channels=channels,
                                        rate=rate,
                                        output=True
                                    )
        while not lock.locked():
            try:
                buff = self.buffer.get(True, 1)
                self.stream.write(buff)
            except Exception: pass #empty buffer
        
        self.stream.stop_stream()
        self.stream.close()
        self._audiorender.terminate()
    
    def play(self, channels, rate, audio_format=pyaudio.paInt16):
        self.lock.acquire() # stop current streams
        if not self.play_thread:
            self.play_thread = threading.Thread( 
                            target = self._play,
                            args = (self.lock, int(channels), int(rate), audio_format)
                            )
            self.lock.release()
            self.play_thread.start()
        else:
            self.buffer = Queue()
    
    def stop(self):
        if DEBUG: print "* stopping audio stream"
        self.lock.acquire()
    
    def to_buffer(self, data):
        self.buffer.put(data)
        
    

class AudioSocket( socket.socket ):
    
    def __init__(self, family=socket.AF_INET, type=socket.SOCK_STREAM):
        socket.socket.__init__(self, family, type)
        try:
            self.connect( CONNECTION )
            if DEBUG: print "* added to server stream"
        except Exception:
            print "ERROR: not able to connect to server"
        
        self.player = Player()
    
    def _wait_response(self, block_size = 1024, standyby_minutes = 30):
        try:
            ready = select.select([self], [], [], standyby_minutes*60)
            if ready[0]:
                return self.recv(block_size)
        except select.error:
            if DEBUG: print "* starting to shutdown due to standby"
            self._do_action( STOP )
    
    def _do_action(self, msg):
        if STOP == msg.lower():
            if DEBUG: print "* shutdown"
            self.run = False
            self.player.stop()
            self.close()
        elif PLAYING in msg.lower(): 
            self.is_receive = True
            self.player.play(*msg.split(",")[1:])
    
    def start(self):
        self.run = True          # listen for socket data
        self.is_receive = False  # socket data is audio stream
        
        try:
            while self.run:
                if self.is_receive: self.player.to_buffer(self._wait_response()) 
                else: 
                    self._do_action( self._wait_response() )
        except KeyboardInterrupt:
            self.sendall( BYE )
            self._do_action( STOP )
    
    def stop(self):
        self.sendall( BYE ) # server
        self._do_action( STOP ) #locally
        
a = AudioSocket()
a.start()
a.stop()