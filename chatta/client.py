import uuid
import common
import socket
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

    def EventLoop(self):
        """The main event loop to render messages received from the server"""
        #TODO, Receive events and render the GUI
        
        try:
            while True:
                msg = self.msocket.RecvSecure()
                
                if msg > len(self.BasicMsg) and msg[0:len(self.BasicMsg)] == self.BasicMsg:
                    self.tui.ExternalMessageAppend(msg[len(self.BasicMsg) + 1:]) #+1 for space separation
                
        except ValueError:
            return

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
            self.tui = tui.UserTUI()
            self.tui.Start()
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
                
                while True:
                    key = self.tui.main_window.getch()
                    if key == 27:
                        self.socket.Close()
                        self.msocket.Close()
                        break #Break on escape key
                    elif key == curses.KEY_ENTER or key == 10 or key == 13:
                        self.Send(self.BasicMsg + ' ' + self.tui.GetMessage())
                        self.tui.MessageClear()
                    elif key == curses.KEY_RESIZE:
                        self.tui.Redraw()
                    elif key == curses.erasechar() or key == 8: # Note backspace value varation beween shells
                        self.tui.MessageClearOne()
                    else:
                        self.tui.MessageAppend(key) 
            
            else:
                self.socket.Close()
        
        except Exception as e:
            traceback.print_exc(e)
        
        self.tui.End()
        return


def Main():
    """Entry point for the application"""
    
    try:
        global tui, curses
        import tui, curses
    except:
        print('No curses library is installed. Cannot use client without it!')
        return
    
    chatta = ChattaClient()
    chatta.Run()
    return

if __name__ == '__main__':
    Main()

