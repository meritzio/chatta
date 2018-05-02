import socket
import sys, os, traceback
import hashlib, fractions, math
import threading, time
import subprocess

import keyExchangeGenerators
from Crypto.Random import random, get_random_bytes   #pycryptodome dependency
from Crypto.Cipher import AES      #pycryptodome dependency
from Crypto.Util import number     #pytcrptodome dependency

class DiffieHellman(object):
    """An implementation of the Diffie-Hellman key exchange tool"""
    
    KeyLength  = 3072
    Ack        = 'ACK'.encode()

    def __init__(self):
        self.SharedPrime    = -1   # p - Prime to be computed at runtime
        self.SharedBase     = -1   # g - Shared base to be computed at runtime (primitive root modulo)
        self.SharedSecret   = -1   # To be computed from dialog
        self.cipherKey      = None #key driven by shared secret
        self.PrimeCache     = keyExchangeGenerators.dhGroups
        return
    
    def IsPrime(self, n):
        return all(n % i for i in xrange(2, n))
    
    def RandKey(self):
        sr = random.StrongRandom()
        return sr.getrandbits(self.KeyLength)
    
    def RandomPrime(self):
        return random.choice(self.PrimeCache)
    
    def PrimitiveRoots(self, modulo):
        """Get the primitive roots of the modulo"""
        modRange = range(1, modulo)
        required = {x for x in modRange if fractions.gcd(x, modulo)}
        return [g for g in modRange if required == {pow(g, powers, modulo) for powers in modRange}]
    
    def send(self, socket, data, bufferSize):
        """Send data securely"""
        IV = get_random_bytes(16)
        cipher = AES.new(self.cipherKey, AES.MODE_CFB, IV)
        ciphertext = cipher.encrypt(data)
        socket.send(IV)
        socket.recv(bufferSize)
        if len(ciphertext) > bufferSize: raise Exception("Out of size!")
        socket.send(str(len(ciphertext)).encode())
        socket.recv(bufferSize)
        socket.send(ciphertext)
        socket.recv(bufferSize)
        return
    
    def recv(self, socket, bufferSize):
        """Receive secure data"""
        IV = socket.recv(bufferSize)
        cipher = AES.new(self.cipherKey, AES.MODE_CFB, IV)
        socket.send(self.Ack)
        cipherLen = int(socket.recv(bufferSize).decode())
        socket.send(self.Ack)
        ciphertext = ''.encode()
        i = 0
        while i != cipherLen:
            data = socket.recv(bufferSize)
            ciphertext += data
            i += len(data)
        
        socket.send(self.Ack)
        data = cipher.decrypt(ciphertext)
        return data
    
    def sendStr(self, socket, string, bufferSize=1024):
        """Send a string securely"""
        return self.send(socket, string.encode(), bufferSize)
    
    def recvStr(self, socket, bufferSize=1024):
        """Receive a string securely"""
        return self.recv(socket, bufferSize).decode()

    def ExchangeClient(self, socket, bufferSize=4096):
        """Perform a key exchange with the given server to make a shared secret"""
        self.SharedPrime = number.bytes_to_long(socket.recv(bufferSize))
        socket.send(self.Ack)
        self.SharedBase = number.bytes_to_long(socket.recv(bufferSize))
        socket.send(self.Ack)
        
        key = self.RandKey() #client secret
        compound = number.bytes_to_long(socket.recv(bufferSize))
        socket.send(self.Ack)
        socket.recv(bufferSize)
        socket.send(number.long_to_bytes(pow(self.SharedBase, key, self.SharedPrime)))
        socket.recv(bufferSize)
        self.SharedSecret = pow(compound, key, self.SharedPrime) #symmetric compute
        self.cipherKey = hashlib.sha256(number.long_to_bytes(self.SharedSecret)).digest()
        return
    
    def ExchangeServer(self, socket, bufferSize=4096):
        """Perform a key exchange with the given client to make a shared secret"""
        self.SharedPrime, self.SharedBase = self.RandomPrime()
        socket.send(number.long_to_bytes(self.SharedPrime))
        socket.recv(bufferSize)
        socket.send(number.long_to_bytes(self.SharedBase))
        socket.recv(bufferSize)
        
        key = self.RandKey() #client secret
        socket.send(number.long_to_bytes(pow(self.SharedBase, key, self.SharedPrime)))
        socket.recv(bufferSize)
        socket.send(self.Ack)
        compound = number.bytes_to_long(socket.recv(bufferSize))
        socket.send(self.Ack)
        self.SharedSecret = pow(compound, key, self.SharedPrime) #symmetric compute
        self.cipherKey = hashlib.sha256(number.long_to_bytes(self.SharedSecret)).digest()
        return
    
    def UnitTestServer(self):
        """Initiate a server unit test in conjuction with the client unit test"""
        print('--server--')
        print('server pid is ' + str(os.getpid()))
        try:
            s = socket.socket()
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(('', 25692))
            s.listen(1)
            c, addr = s.accept() #get client socket and address
            s.close()
            self.ExchangeServer(c)
            print("prime index: " + str(self.PrimeCache.index((self.SharedPrime, self.SharedBase))))
            print('Shared secret: ' + str(self.SharedSecret))
            self.sendStr(c, 'An encrypted message')
            msg = self.recvStr(c)
            if msg == 'Thanks for sharing':
                print('Client message received OK')
            else:
                raise Exception('Failed to decrypt client message!')
            c.close()
        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            c.close()
            return False
        
        return True

    def UnitTestClient(self):
        """Initiate a client unit test in conjuction with the server unit test"""
        print('\n--client')
        print('client pid is ' + str(os.getpid()))
        try:
            s = socket.socket()
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.connect((socket.gethostbyname('localhost'), 25692))
            self.ExchangeClient(s)
            print('Shared secret: ' + str(self.SharedSecret))
            msg = self.recvStr(s)
            if msg == 'An encrypted message':
                print('Server message received OK')
            else:
                raise Exception('Failed to decrypt server message!')
            
            self.sendStr(s, 'Thanks for sharing')
            s.close()
            
        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            s.close()
            return False
        
        return True
    
    @staticmethod
    def UnitTest():
        """Run a unit test to ensure that key exchange communications are working"""
        print('--Running key exchange unit test--')
        server = DiffieHellman()
        t0 = threading.Thread(target=server.UnitTestServer)
        t0.start()
        time.sleep(0.1)
        logname = 'dhlog'
        with open(logname, 'w') as stdout:
            subprocess.call(['python', 'keyExchange.py', 'client'], stdout=stdout)
        
        f = open(logname,'r') #Client logfile
        print(f.read())
        f.close()
        os.remove(logname)
        return



if __name__ == '__main__':
    if len(sys.argv) > 1:
        try:
            arg = sys.argv[1]
            
            if arg == 'client':
                client = DiffieHellman()
                if client.UnitTestClient():
                    print('Success.')
                else:
                    print('Fail.')
            else:
                print('Argument \"' + arg + '\" not recognised')
        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            print('Fail.')

    else:
        DiffieHellman.UnitTest()

