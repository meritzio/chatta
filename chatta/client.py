import uuid
import common
import threading
import traceback
import securesocket

class ChattaClient(common.ChattaBase):
    """The chatta client application"""
    
    def __init__(self):
        """Construct a chatta client session"""
        common.ChattaBase.__init__(self)
        self.msocket = securesocket.SecureSocket() #Messaging socket
        return
    
    def Send(self, message):
        """Send a message`"""
        self.socket.SendSecure(message)
        return
    
    def Receive(self):
        """Receive a message`"""
        return self.socket.RecvSecure()

    def StartTUI(self):
        """Start the curses TUI"""
        self.tui = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.tui.keypad(True)
        return

    def EndTUI(self):
        """End the curses TUI"""
        if not self.tui: #If TUI not initialised
            return
        
        curses.nocbreak()
        self.tui.keypad(False)
        curses.echo()
        curses.endwin()
        return

    def EventLoop(self):
        """The main event loop to render messages received from the server"""
        #TODO, Receive events and render the GUI
        return

    def Run(self):
        """Start the client application"""
        
        if not self.settings.Valid():
            print('Incorrect settings! Check out "' + 
                   common.ChattaSettings.SettingsFileName + '" and try again')
            return
        
        #TODO User initiation, getting chatroom state from server connection
        # User input loop, curses library GUI rendered chatroom
        try:
            self.StartTUI()
            host = self.settings.host
            port = self.settings.port
            self.socket.Connect(host, port)
            guid = str(uuid.uuid4())
            self.Send(self.UserEntry + ' ' + guid) #Inform of entry
            ack = self.Receive() #Wait for acknowledgment
            
            if ack == self.Ack:
                self.msocket.Connect(host, port)
                self.msocket.SendSecure(self.EventLine + ' ' + guid)
                t = threading.Thread(target=self.EventLoop)
                t.start()
                
                msg = ''
                while True:
                    key = self.tui.getch()
                    if key == 27:
                        self.socket.Close()
                        self.msocket.Close()
                        break #Break on escape key
                    elif key == 10:
                        self.tui.echochar(key) 
                        self.Send(self.BasicMsg + ' ' + msg)
                        msg = ''
                    else:
                        self.tui.echochar(key) 
                        msg += chr(key)
            
            else:
                self.socket.Close()
        
        except Exception as e:
            traceback.print_exc(e)
        
        self.EndTUI()
        return


def Main():
    """Entry point for the application"""
    
    try:
        global curses
        import curses
    except:
        print('No curses library is installed. Cannot use client without it!')
        return
    
    chatta = ChattaClient()
    chatta.Run()
    return

if __name__ == '__main__':
    Main()

