import socket

target = "10.135.235.13"
open_ports = []

for port in range(1, 1025):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.5)
    result = s.connect_ex((target, port))
    if result == 0:
        open_ports.append(port)
    s.close()

print("Open ports:", open_ports)