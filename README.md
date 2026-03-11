# Port Scanner [V1]

A simple TCP port scanner built from scratch using Python's standard library. No third-party packages required.

---

## What it does

Scans a target IP address for open TCP ports across the range 1–1024 and prints a summary of all open ports found.

---

## How it works

1. Creates a TCP socket for each port using Python's built-in `socket` module
2. Attempts a connection via `connect_ex()` — returns `0` if the port is open, an error code if not
3. Collects all open ports into a list
4. Prints the results when the scan is complete

---

## Why TCP only

TCP uses a 3-way handshake (SYN → SYN-ACK → ACK) which forces the target to respond. This gives a clean, reliable answer for every port — open, closed, or filtered. UDP has no handshake, so scanning it is slower, ambiguous, and much harder to interpret. TCP is the right starting point.

---

## Requirements

- Python 3.x
- No external libraries — standard library only

---

## Usage

```bash
python scannerV1.py
```

Edit the `target` variable inside the script to point at your chosen IP:

```python
target = "127.0.0.1"   # localhost
# or
target = "192.168.1.x" # another device on your network
```

---

## Performance

| Setting | Value |
|---|---|
| Port range | 1 – 1024 |
| Timeout per port | 0.5 seconds |
| Worst-case scan time | 1024 × 0.5s = **~8.5 minutes** |
| Typical scan time | Much faster — most ports respond (or fail) instantly |

> The 8-minute worst case only happens if every single port is filtered and nmap has to wait the full 0.5s timeout on all 1024 ports. In practice, closed ports respond immediately with a RST packet, so the scan usually completes in seconds.

---

## Example output

```
Scanning 192.168.1.10 ...
Port 22 is OPEN
Port 80 is OPEN
Port 443 is OPEN

Scan complete.
Open ports: [22, 80, 443]
```

---

## Project structure

```
port_scanner/
└── scannerV1.py    # main scanner script
└── README.md       # this file
```

---

## Concepts used

| Concept | Purpose |
|---|---|
| `socket.socket()` | Creates a raw TCP connection tool |
| `AF_INET` | Specifies IPv4 addressing |
| `SOCK_STREAM` | Specifies TCP (stream-based, reliable) |
| `connect_ex()` | Returns error code instead of raising exception |
| `settimeout()` | Prevents hanging on filtered ports |
| `range()` | Iterates through port numbers 1–1024 |
| `list.append()` | Collects open ports as scan progresses |

---

## Roadmap

- **V2** — Add banner grabbing (identify what service is running on each open port)
- **V3** — Add threading for faster scans
- **V4** — Add command-line arguments for custom IP, port range, and timeout

---

## Legal notice

Only scan systems you own or have explicit permission to scan. Unauthorised port scanning may be illegal in your jurisdiction.
