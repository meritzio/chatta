import os
import json
import securesocket


class ChattaSettings(object):
    """Access the chatta settings"""

    settings_file_name = 'settings.json'
    host_field = 'Host'
    port_field= 'Port'

    def __init__(self):
        self.host = None
        self.port = -1

        if not os.path.isfile(self.settings_file_name):
            return

        with open(self.settings_file_name, 'r') as f:
            data = f.read()

        try:
            data = json.loads(data)
            self.host = str(data[self.host_field])
            self.port = int(data[self.port_field])
        except JSONDecodeError:
            return

        return

    def Valid(self):
        """Verify the user settings are valid"""
        # TODO sanitise host entry and type check
        return self.host and self.port > 0


class ChattaBase(object):
    """The common properties and functions between the server and client"""

    Ack = 'ACK'
    UserEntry = 'CHATTA'
    EventLine = 'EVENTS'
    BasicMsg = 'MESSAGE'

    def __init__(self):
        self.settings = ChattaSettings()
        self.socket = securesocket.SecureSocket()
        return
