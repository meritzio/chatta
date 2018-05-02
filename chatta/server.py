import common
import traceback

class ChattaServer(common.ChattaBase):
    """The chatta server node"""

    def __init__(self):
        """Construct a chatta node"""
        common.ChattaBase.__init__(self)
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
                    sock, addr = self.socket.Accept() #Connection should thread off from here
                    print(str(addr) + " connected")
                    sock.SendSecure("Hello!")
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

