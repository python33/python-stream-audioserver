from SocketServer import ThreadingMixIn, UDPServer

class RequestHandler( StreamRequestHandler ):
    # her skal det skje noe hver gang en bruker kobler seg på serveren
    pass

class StreamServer( UDPServer ):
    # her skal vi bare starte UDP serveren
    pass

class ThreadedStreamServer(ThreadingMixIn, PipeServer):
    # denne skal vi ikke gjøre noe med
    pass