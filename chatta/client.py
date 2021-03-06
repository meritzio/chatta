from builtins import input #py2 and py3 input support
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
        self.username = ''
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
                if msg > len(self.BasicMsg) and msg[0:len(self.BasicMsg)] == self.BasicMsg: #Basic message command
                    self.tui.ExternalMessageAppend(msg[len(self.BasicMsg) + 1:]) #+1 for space separation
                
        except ValueError:
            return

        return

    def UserLoop(self):
        """The user key capture loop"""
        while True:
            key = self.tui.main_window.getch()
            if key == 27:
                self.socket.Close()
                self.msocket.Close()
                break # Break on escape key
            elif key == curses.KEY_ENTER or key == 10 or key == 13:
                self.Send(self.BasicMsg + ' ' + self.tui.GetMessage())
                self.tui.MessageClear()
            elif key == curses.KEY_RESIZE:
                self.tui.Redraw()
            elif key == curses.erasechar() or key == 8 or key == 263: # Note backspace value varation beween shells
                self.tui.MessageClearOne()
            elif key == curses.KEY_HOME or key == curses.KEY_END:
                self.tui.MoveEdge(key == curses.KEY_HOME)
            elif key == curses.KEY_LEFT or key == curses.KEY_RIGHT:
                self.tui.Move(key == curses.KEY_LEFT)
            elif key == curses.KEY_UP or key == curses.KEY_DOWN:
                y, x = self.tui.main_window.getyx()
                # TODO swap cursor between windows
            else:
                try:
                    chr(key).encode('utf-8') # Check in utf-8 range by parsing
                    self.tui.MessageAppend(key) 
                except UnicodeEncodeError:
                    continue
        return

    def ValidUsername(self, value):
        """Check a username is valid"""
        if len(value) < 3: return False

        for v in value:
            if not v.isalpha() and not v.isdigit():
                return False

        return True

    def Setup(self):
        """Get valid username and other required auth from the user"""
        
        value = ''
        while not self.ValidUsername(value):
            value = input('Enter a username: ')
            assert isinstance(value, str)
        
        self.username = value
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
            self.Send(' '.join([self.UserEntry, guid, self.username])) #Inform of entry
            ack = self.Receive() #Wait for acknowledgment
            
            if ack == self.Ack:
                self.msocket.Connect(host, port)
                self.msocket.SendSecure(self.EventLine + ' ' + guid)
                t = threading.Thread(target=self.EventLoop)
                t.start()
                self.UserLoop()    
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
    chatta.Setup()
    chatta.Run()
    return

if __name__ == '__main__':
    Main()

