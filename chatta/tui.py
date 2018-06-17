import curses
import curses.textpad

class UserTUI(object):
    """Responsible for drawing the client messages in a TUI format"""

    def __init__(self):
        self.main_window = None
        self.message = list() # list of key integers corresponding to characters
        self.ext_messages = list() # list of strings from external messages (TODO color storage, future)
        self.message_box_x = -1
        self.message_box_y = -1
        self.line_max = 20
        self.win_offset_x = 2
        self.win_offset_y = 1
        self.msg_box_offset_x = 4
        return
    
    def Start(self):
        """Start the curses TUI"""
        self.main_window = curses.initscr()
        curses.start_color()
        curses.noecho()
        curses.cbreak()
        self.main_window.keypad(True)
        self.Redraw(False)
        self.main_window.move(self.message_box_y, self.msg_box_offset_x)
    
    def End(self):
        """End the curses TUI"""
        if not self.main_window: #If TUI not initialised
            return
        
        curses.nocbreak()
        self.main_window.keypad(False)
        curses.echo()
        curses.endwin()
        return
    
    def DrawMessages(self):
        """Draw all received messages into the message box"""
        # Redraw region with messages
        oY, oX = self.main_window.getyx()
        height, width = self.main_window.getmaxyx()
        y, x = (self.win_offset_y + 1, self.win_offset_x + 1)
        y0, x0 = (y, x)
        yL, xL = (min(self.line_max, height - self.message_box_y - y0), width - x0) #Limiting bounds of 0 and L for messages
        
        # Print messages in screen bounds
        for msg in self.ext_messages:
            for character in msg:
                if msg == '\n': # Put spaces until the next line
                    while x < xL:
                        self.main_window.addch(y, x, ' ')
                        x += 1
                    x = x0
                    y += 1
                elif msg == '\r': # Ignore win return carriage
                    continue
                else:
                    self.main_window.addch(y, x, character) # Add the character
                    x += 1
            x = x0
            y += 1
        
        # Clear remaining screen with empty space
        while y < yL:
            while x < xL:
                self.main_window.addch(y, x, ' ')
                x += 1
            x = x0
            y += 1
        
        self.main_window.move(oY, oX)
        return
    
    def MoveEdge(self, start):
        """Move the cursor to the edge of the message"""
        y, x = self.main_window.getyx()
        if start:
            self.main_window.move(y, self.msg_box_offset_x)
        else:
            self.main_window.move(y, self.msg_box_offset_x + len(self.message))
        return
    
    def Move(self, left):
        """Move the cursor around the the message"""
        y, x = self.main_window.getyx()
        x += -1 if left else 1
        self.main_window.move(y, x)
        return

    def ExternalMessageLines(self):
        """Get the number of lines from external messages"""
        lines = 0
        for msg in self.ext_messages:
            lines += msg.count('\n') + 1
        return lines
    
    def ExternalMessageAppend(self, message):
        """Draw a received message onto the user board"""
        #TODO overflow prevention
        self.ext_messages.append(message)

        lines = self.ExternalMessageLines()
        while lines > self.line_max:   
            self.ext_messages.pop(0)
            lines = self.ExternalMessageLines()
        
        self.DrawMessages()
        self.main_window.refresh()
        return

    def UpdateDims(self):
        """Update the dimensios of the panels"""
        height, width = self.main_window.getmaxyx()
        self.message_box_y = 2 * height/3
        self.message_box_x = 2 * width/3
        return

    def Redraw(self, refresh=True):
        """Redraw the TUI elements"""
        y0, x0 = self.main_window.getyx()
        height, width = self.main_window.getmaxyx()
        self.UpdateDims()
        self.main_window.clear()
        curses.textpad.rectangle( #The global pane
            self.main_window,
            self.win_offset_y,
            self.win_offset_x,
            height - self.win_offset_y,
            width - self.win_offset_x
            )
        curses.textpad.rectangle( #The RHS info pane
            self.main_window,
            self.message_box_y - 1,
            self.message_box_x,
            height - 2,
            width - 3
            )
        curses.textpad.rectangle( #The bottom left message pane
            self.main_window,
            self.message_box_y - 1,
            3,
            height - 2,
            width - 3
            )
        
        self.DrawMessages()
        self.DrawMessage()
        self.main_window.move(y0, x0)
        if refresh: self.main_window.refresh()
        return
    
    def GetMessageOffset(self):
        """Get the YX offset of the current message"""
        y = 0 #Currently no newline support, just sends message
        x = len(self.message)
        return (y, x)
    
    def GetMessage(self):
        """Get the message from the message box"""
        return ''.join([chr(x) for x in self.message])
    
    def DrawMessage(self):
        """Draw the message in the message box"""
        height, width = self.main_window.getmaxyx()
        x = self.msg_box_offset_x
        y = self.message_box_y
        
        for m in self.message:
            self.main_window.addch(self.message_box_y, x, m)
            x += 1
        return
    
    def MessageAppend(self, intchar):
        """Add a character to the message box"""
        # TODO overflow prevention
        y, x = self.main_window.getyx()
        y0, x0 = (y, x)
        x -= self.msg_box_offset_x
        x = min(len(self.message), x) # Clamp
        x = max(x, 0)
        self.message.insert(x, intchar) # Insert at the cursor position
        self.DrawMessage()
        self.main_window.move(y0, x0 + 1)
        self.main_window.refresh()
        return
    
    def MessageClear(self):
        """Clear the message box"""
        while len(self.message): #TODO More efficient clear method
            self.MessageClearOne()
        return
    
    def MessageClearOne(self):
        """Peform a backspace"""
        height, width = self.main_window.getmaxyx()
        lineY, lineX = self.GetMessageOffset()
        if lineX + lineY == 0: return
        
        self.main_window.addch(
            self.message_box_y + lineY,
            3 + lineX,
            ' '
            )
        self.main_window.move(
            self.message_box_y + lineY,
            3 + lineX,
            )
        self.message.pop()
        return
    
    @staticmethod
    def Main():
        try:
            tui = UserTUI()
            tui.Start()
        except Exception as e:
            import traceback
            traceback.print_exc(e)
        finally:
            tui.End()
        return

if __name__ == '__main__':
    UserTUI.Main()

