import threading

class ChattaUser(object):
    """Represents a user in the chatroom"""
    
    def __init__(self, guid, insock, addr):
        self.guid   = guid
        self.addr   = addr
        self.insock = insock #The User's Input Socket
        self.msock  = None   #The User's event receiving
        self.sockLock = threading.Lock()
        return
    
    def Event(self, message):
        """Inform the users event loop"""
        
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


