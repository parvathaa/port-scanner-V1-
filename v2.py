import socket

target = "10.135.235.13"
open_ports = []

print(f"Scanning {target} ...\n")

for port in range(1, 1025):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)

    result = s.connect_ex((target, port))

    if result == 0:
        open_ports.append(port)
        banner = "No banner"

        try:
            # try receiving immediately — chatty services talk first
            s.send(b"HEAD / HTTP/1.0\r\n\r\n")
            banner = s.recv(1024).decode(errors="ignore").strip()
        except:
            banner = "No banner"

        print(f"Port {port} OPEN — {banner}")

    s.close()

print(f"\nScan complete.")
print(f"Open ports: {open_ports}")
