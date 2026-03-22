import socket
import threading
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

open_ports = []
lock = threading.Lock()

def scan_port(ip, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            result = s.connect_ex((ip, port))
            if result == 0:
                banner = ""
                try:
                    s.settimeout(1)
                    banner = s.recv(1024).decode().strip()
                except:
                    pass
                with lock:
                    open_ports.append(port)
                    if banner:
                        print(f"[+] {port:>5}/tcp   OPEN   | {banner}")
                    else:
                        print(f"[+] {port:>5}/tcp   OPEN")
    except socket.error:
        pass

def run_scan(ip, start_port, end_port, max_workers=200):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for port in range(start_port, end_port + 1):
            executor.submit(scan_port, ip, port)

target_host = "127.0.0.1"
start_port  = 1
end_port    = 1024

try:
    target_ip = socket.gethostbyname(target_host)
except socket.gaierror:
    print(f"[-] Cannot resolve: {target_host}")
    sys.exit(1)

print(f"\n[*] Target  : {target_host} ({target_ip})")
print(f"[*] Ports   : {start_port}-{end_port}")
print(f"[*] Threads : 200")
print(f"[*] Started : {datetime.now().strftime('%H:%M:%S')}")
print("=" * 50)

run_scan(target_ip, start_port, end_port)

print("=" * 50)
print(f"[*] Finished: {datetime.now().strftime('%H:%M:%S')}")
print(f"[*] Open ports: {sorted(open_ports)}")
