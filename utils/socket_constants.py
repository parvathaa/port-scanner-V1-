#this lists down every integer constant defined in the socket module on your system

import socket

for name in dir(socket):
    if name.isupper():  # constants are ALL_CAPS
        value = getattr(socket, name)
        if isinstance(value, int):
            print(f"{name} = {value}")
