import os
import json
import securesocket

class ChattaSettings(object):
    """Access the chatta settings"""

    SettingsFileName = 'settings.json'
    HostField = 'Host'
    PortField = 'Port'
    
    def __init__(self):
        self.host = None
        self.port = -1
        
        if not os.path.isfile(self.SettingsFileName):
            return
        
        f = open(self.SettingsFileName, 'r')
        data = f.read()
        f.close()
        
        try:
            data = json.loads(data)
            self.host = str(data[self.HostField])
            self.port = int(data[self.PortField])
        except JSONDecodeError:
            return
        
        return

    def Valid(self):
        """Verify the user settings are valid"""
        #TODO sanitise host entry and type check
        return self.host and self.port > 0


class ChattaBase(object):
    """The common properties and functions between the server and client"""


    def __init__(self):
        self.settings = ChattaSettings()
        self.socket = securesocket.SecureSocket()
        return


