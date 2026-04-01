import socket
import threading
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import subprocess
import re
import argparse
import errno

#service signatures

SERVICE_SIGNATURES = {
    r"SSH-.*OpenSSH": "SSH",
    r"SSH-": "SSH",
    r"HTTP/": "HTTP",
    r"Server:.*nginx": "HTTP (nginx)",
    r"Server:.*Apache": "HTTP (Apache)",
    r"FTP": "FTP",
    r"SMTP": "SMTP",
    r"POP3": "POP3",
    r"IMAP": "IMAP",
}

def match_service(banner):
    for pattern, service in SERVICE_SIGNATURES.items():
        if re.search(pattern, banner, re.IGNORECASE):
            return service
    return "Unknown"


open_ports = []  
filtered_ports = []

lock = threading.Lock()
progress_lock = threading.Lock()

total_ports = 0
scanned_ports = 0
start_time = None


#progress bar

def update_progress():
    global scanned_ports

    with progress_lock:
        scanned_ports += 1

        percent = (scanned_ports / total_ports) * 100
        elapsed = (datetime.now() - start_time).total_seconds()

        rate = scanned_ports / elapsed if elapsed > 0 else 0
        remaining = total_ports - scanned_ports
        eta = remaining / rate if rate > 0 else 0

        bar_length = 20
        filled = int(bar_length * scanned_ports // total_ports)
        bar = ">" * filled + "-" * (bar_length - filled)

        print(f"\r[{bar}] {percent:5.1f}% | {int(rate)} p/s | ETA: {int(eta)}s", end="")


#scan

def scan_port(ip, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            result = s.connect_ex((ip, port))

            if result == 0:
                banner = ""
                service = "Unknown"

                try:
                    s.settimeout(1)
                    banner = s.recv(1024).decode(errors="ignore").strip()
                    if banner:
                        service = match_service(banner)
                except:
                    pass

                with lock:
                    open_ports.append({
                        "port": port,
                        "service": service,
                        "banner": banner
                    })

            elif result == errno.ECONNREFUSED:
                pass

            else:
                with lock:
                    filtered_ports.append(port)

    except socket.timeout:
        with lock:
            filtered_ports.append(port)

    except socket.error:
        pass

    finally:
        update_progress()


def run_scan(ip, start_port, end_port, max_workers=100):
    futures = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for port in range(start_port, end_port + 1):
            futures.append(executor.submit(scan_port, ip, port))

        for future in futures:
            future.result()


#ttl os hint

def get_ttl(target_ip):
    try:
        output = subprocess.check_output(
            ["ping", "-c", "1", target_ip],
            stderr=subprocess.DEVNULL
        ).decode()
        match = re.search(r"ttl=(\d+)", output, re.IGNORECASE)
        if match:
            return int(match.group(1))
    except:
        return None


def ttl_os_hint(ttl):
    if ttl is None:
        return "unknown"
    if ttl <= 64:
        return "Linux/macOS"
    elif ttl <= 128:
        return "Windows"
    elif ttl <= 255:
        return "Network device"
    return "unknown"


#argparse 

parser = argparse.ArgumentParser(description="Port Scanner")

parser.add_argument("--target", help="Target IP or hostname")
parser.add_argument("--ports", default="1-1024", help="Port range e.g. 1-1024")
parser.add_argument("--threads", default=100, type=int, help="Number of threads")

args = parser.parse_args()

target_host = args.target or input("[?] Enter target IP or hostname: ").strip()

if not target_host:
    print("[-] Target cannot be empty.")
    sys.exit(1)

try:
    start_port, end_port = map(int, args.ports.split("-"))
    if start_port < 1 or end_port > 65535 or start_port > end_port:
        raise ValueError
except ValueError:
    print("[-] Invalid port range. Use format: 1-1024")
    sys.exit(1)

max_threads = args.threads


#main

try:
    target_ip = socket.gethostbyname(target_host)
except socket.gaierror:
    print(f"[-] Cannot resolve: {target_host}")
    sys.exit(1)

ttl = get_ttl(target_ip)
os_hint = ttl_os_hint(ttl)

total_ports = end_port - start_port + 1
start_time = datetime.now()

print(f"\n[*] Target  : {target_host} ({target_ip})")
print(f"[*] OS Hint : {os_hint} (TTL={ttl})")
print(f"[*] Ports   : {start_port}-{end_port}")
print(f"[*] Threads : {max_threads}")
print(f"[*] Started : {start_time.strftime('%H:%M:%S')}")
print("=" * 50)

run_scan(target_ip, start_port, end_port, max_workers=max_threads)

print("\n" + "=" * 50)
print(f"[*] Finished: {datetime.now().strftime('%H:%M:%S')}")


#results

print("\n[*] Open Ports:")
for entry in sorted(open_ports, key=lambda x: x["port"]):
    if entry["banner"]:
        print(f"[+] {entry['port']:>5}/tcp OPEN  | {entry['service']} | {entry['banner']}")
    else:
        print(f"[+] {entry['port']:>5}/tcp OPEN  | {entry['service']}")

print(f"\n[*] Filtered ports: {len(filtered_ports)}")