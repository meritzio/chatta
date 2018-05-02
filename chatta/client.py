import common
import traceback

class ChattaClient(common.ChattaBase):
    """The chatta client application"""
    
    def __init__(self):
        """Construct a chatta client session"""
        common.ChattaBase.__init__(self)
        return
    
    def Send(self, message):
        """Send a message`"""
        self.socket.SendSecure(message)
        return
    
    def Receive(self):
        """Receive a message`"""
        return self.socket.RecvSecure()

    def Run(self):
        """Start the client application"""
        
        if not self.settings.Valid():
            print('Incorrect settings! Check out "' + 
                   common.ChattaSettings.SettingsFileName + '" and try again')
            return
        
        #TODO User initiation, getting chatroom state from server connection
        # User input loop, curses library GUI rendered chatroom
        try:
            host = self.settings.host
            port = self.settings.port
            self.socket.Connect(host, port)
            msg = self.Receive()
            print(msg)
            
        except Exception as e:
            traceback.print_exc(e)
            return
        
        return


def Main():
    """Entry point for the application"""
    chatta = ChattaClient()
    chatta.Run()
    return

if __name__ == '__main__':
    Main()

