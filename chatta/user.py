import threading
from common import ChattaBase

class ChattaUser(object):
    """Represents a user in the chatroom"""
    
    def __init__(self, guid, username, insock, addr):
        self.guid   = guid
        self.name   = username
        self.addr   = addr
        self.insock = insock #The User's Input Socket
        self.msock  = None   #The User's event receiving
        self.sockLock = threading.Lock()
        return
    
    def IsEvent(self, mType, message):
        """Verify a message is of the type specified"""
        return len(message) > len(mType) and message[:len(mType)] == mType

    def Event(self, message):
        """Inform the users event loop"""
        self.sockLock.acquire()
        
        if self.IsEvent(ChattaBase.BasicMsg, message):
            self.msock.SendSecure(ChattaBase.BasicMsg + ' ' + self.name + ': ' + message[len(ChattaBase.BasicMsg) + 1:])
        
        self.sockLock.release()
        return

    def EndSession(self):
        """End the users session"""
        self.sockLock.acquire()
        self.msock.Close()
        self.insock.Close()
        self.sockLock.release()
        return

    def Receive(self):
        """Wait for and return user input"""
        msg = self.insock.RecvSecure()
        return msg

    def HasEventSocket(self):
        """Check if the user has an event socket yet"""
        self.sockLock.acquire()
        hasSocket = self.msock is not None
        self.sockLock.release()
        return hasSocket
    
    def SetEventSocket(self, msock):
        """Set the users event socket threadsafely"""
        self.sockLock.acquire()
        self.msock = msock
        self.sockLock.release()
        return


