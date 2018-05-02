import socket
from keyExchange import DiffieHellman

class SecureSocket(object):
    """Represents a socket implementation that can perform secure exchanges"""
    
    def __init__(self, sock=None):
        self.socket = socket.socket() if not sock else sock
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.dh = DiffieHellman()
        return

    def KeyExchangeServer(self):
        self.dh.ExchangeServer(self.socket, 4096)
        return
    
    def KeyExchangeClient(self):
        self.dh.ExchangeClient(self.socket, 4096)
        return
    
    def Bind(self, host, port):
        self.socket.bind((host, port))
        return

    def Listen(self, count):
        self.socket.listen(count)
        return
    
    def Accept(self):
        sock, addr = self.socket.accept()
        c = SecureSocket(sock)
        c.KeyExchangeServer()
        return (c, addr)

    def Connect(self, address, port):
        self.socket.connect((address, port))
        self.KeyExchangeClient()
        return

    def SendSecure(self, data, bufferSize=1024):
        self.dh.send(self.socket, data, bufferSize)

    def RecvSecure(self, bufferSize=1024):
        return self.dh.recv(self.socket, bufferSize)

    def getpeername(self):
        """socket wrapper of getpeername"""
        return self.socket.getpeername()
    
    def getsockname(self):
        """socket wrapper of getsockname"""
        return self.socket.getsockname()
    
    def Close(self):
        """socket wrapper of close method"""
        self.socket.close()
        return

