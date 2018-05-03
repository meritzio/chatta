# Chatta

Authors: 
* Sam Woodhead (sam@blueforge.xyz)
* Thomas Deadman

## About
Chatta is a simple application for friends to chat online

## How-To
1. Make sure you setup a 'settings.json' file with the address and port of the chat server
2. Make sure you install the required python libraries for end-to-end encyption ('install_chatta.sh' will do this)
3. If on windows, get a get a [build of curses for your version of python](https://www.lfd.uci.edu/~gohlke/pythonlibs/#curses) and then install it using the command:
```sh
python -m pip install yourVersion.whl
```

## Starting the client
Run the command
```sh
python client.py
```
to connect to the chatroom

## Starting the server
Run the command
```sh
python server.py
```
to begin hosting
or simply click the file in a windows GUI if python file types are correctly setup

