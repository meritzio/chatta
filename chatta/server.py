import common
import threading
import traceback
from user import ChattaUser

class ChattaServer(common.ChattaBase):
    """The chatta server node"""

    def __init__(self):
        """Construct a chatta node"""
        common.ChattaBase.__init__(self)
        self.users = set() #All the users
        self.usrLock = threading.Lock() #Thread save user list lock
        return
    
    def AddUser(self, user):
        """Add a user to the list"""
        self.usrLock.acquire()
        self.users.add(user)
        self.usrLock.release()
        return
    
    def RemoveUser(self, user):
        """Remove a user from the list"""
        self.usrLock.acquire()
        self.users.remove(user)
        self.usrLock.release()
        return

    def GetUser(self, guid):
        """Get the user from their GUID"""
        self.usrLock.acquire()
        
        user = None
        for candidate in self.users: #Match the user
            if candidate.guid == guid:
                user = candidate
                break
        
        self.usrLock.release()
        return user

    def UserSession(self, user):
        """A user thread sessions"""
        
        while not user.HasEventSocket(): #Wait for the user to get their message socket
            continue
        
        print(str(user.addr) + " connected")
        
        while True: #Take user input
            try:
                msg = user.Receive()
                if msg == 'exit': #TODO Example exit loop
                    break
                else:
                    print(msg)
            except Exception:
                break
        
        print(str(user.addr) + "disconnected")
        user.EndSession()
        return

    def Run(self):
        """Begin hosting the server"""
        
        if not self.settings.Valid():
            print('Invalid settings, check your configuration file "' + 
                   common.ChattaSettings.SettingsFileName + '" and try again')
            return
        
        try:
            host = self.settings.host
            port = self.settings.port
            print('Binding to port ' + str(port) + ' on host "' + str(host) + '"...')
            self.socket.Bind(host, port)
            print('Listening...')
            
            #TODO User entry loop implementation (track each user connection on threads)
            # plan how to inform everyone of events
            while True:
                self.socket.Listen(5)
                try:
                    sock, addr = self.socket.Accept()
                    message = sock.RecvSecure() #Receive user
                    print(message)

                    #Socket message stated something invalid to this application, ignore
                    if len(message) < max(len(self.EventLine), len(self.UserEntry)):
                        sock.Close()
                        continue
                    
                    #Parse the GUID
                    if message[:len(self.UserEntry)] == self.UserEntry:
                        guid = message[len(self.UserEntry) + 1:]
                        user = ChattaUser(guid, sock, addr)
                        self.AddUser(user)
                        sock.SendSecure(self.Ack)
                        t = threading.Thread(target=self.UserSession, args=(user,))
                        t.start()
                    elif message[:len(self.EventLine)] == self.EventLine:
                        guid = message[len(self.EventLine) + 1:] #Get the guid
                        user = self.GetUser(guid)                #Get the user
                        if user: user.SetEventSocket(sock)       #Match the socket
                    else:
                        sock.Close()
                        
                except KeyboardInterrupt:
                    print("Shutting down server (closing any connections...)")
                    return
            
        except Exception as e:
            traceback.print_exc(e)
            return
        
        return


def Main():
    """Entry point for the application"""
    chatta = ChattaServer()
    chatta.Run()
    return

if __name__ == '__main__':
    Main()

