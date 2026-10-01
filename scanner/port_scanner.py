import socket
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from pathlib import Path
from datetime import datetime
import argparse

try:
    import resource
except ImportError:  # not available on Windows
    resource = None

DEFAULT_CONFIG = {
    "timeout": 0.3,
    "max_worker": 1600,
    "create_logs": False
}

# File descriptors kept free for stdio, log files, DNS lookups, etc.
FD_HEADROOM = 64

COMMON_PORTS = {
    20: "FTP Data",
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS",
    3306: "MySQL",
    5432: "PostgreSQL"
}

def validate_port(start, end):
    if start.isdigit() and end.isdigit():
        return True
    else: 
        print("Port can only be number.")
        return False
    
def validate_range(start, end):
    if not (1 <= start <= 65535):
        print("Invalid starting port")
        return False

    if not (1 <= end <= 65535):
        print("Invalid ending port")
        return False

    if start > end:
        print("Starting port must be smaller than ending port")
        return False
    
    return True

def scan_port(timeout, ip, port):
    try:
        with socket.socket() as s:
            s.settimeout(timeout)

            latency_start_time = time.perf_counter()
            result = s.connect_ex((ip, port))
            # Stop the clock here so the service lookup isn't counted as latency
            latency_end_time = time.perf_counter()
            service = None

            if result == 0:
                if port in COMMON_PORTS:
                    service = COMMON_PORTS[port]
                else:
                    try:
                        service = socket.getservbyport(port)
                    except OSError:
                        service = "unknown"
                    except Exception:
                        print("Error..")
                        service = "unknown"

                # for future implication
                # try:
                #     s.sendall(b"GET / HTTP/1.1\r\nHost: example.com\r\n\r\n")   # Sends the entire HTTP request header
                #     response = s.recv(1024)   # Receive response
                # except socket.timeout:
                #     banner = "timed out"
                # except Exception as e:
                #     banner = f"error {e}"

                return {"port": port,
                        "service": service,
                        "latency": (latency_end_time - latency_start_time) * 1000}

    # e.g. "Too many open files": report the port as failed instead of crashing the scan
    except OSError as e:
        return {"port": port, "error": str(e)}


def fit_workers_to_fd_limit(workers):
    """
    Each worker holds one socket open, so more workers than the open-file
    limit crashes the scan with "Too many open files". Raise the soft limit
    if the hard limit allows it, otherwise reduce the worker count to fit.
    """
    if resource is None:
        return workers

    needed = workers + FD_HEADROOM
    soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)

    if soft != resource.RLIM_INFINITY and soft < needed:
        new_soft = needed if hard == resource.RLIM_INFINITY else min(needed, hard)
        try:
            resource.setrlimit(resource.RLIMIT_NOFILE, (new_soft, hard))
            soft = new_soft
        except (ValueError, OSError):
            pass

    if soft == resource.RLIM_INFINITY:
        return workers

    return max(1, min(workers, soft - FD_HEADROOM))


def scan(config, ip, start, end):
    # if validate_port(start, end):
    #     start = int(start)
    #     end = int(end)
    
    if not validate_range(start, end):
        return None
    
    ip = socket.gethostbyname(ip)

    workers = min(config['max_worker'], end - start + 1)
    safe_workers = fit_workers_to_fd_limit(workers)

    if safe_workers < workers:
        print(f"Note: the open-file limit only allows {safe_workers} workers "
              f"(requested {workers}). Raise it with `ulimit -n` for faster scans.")
        workers = safe_workers

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(scan_port, config['timeout'], ip, port) for port in range(start, end + 1)]
        data = [f.result() for f in futures]

    failed = [port for port in data if port is not None and "error" in port]
    ports = [port for port in data if port is not None and "error" not in port]

    if failed:
        print(f"Warning: {len(failed)} ports could not be scanned ({failed[0]['error']}). "
              "Results may be incomplete.")

    if config['create_logs']:
        create_logs(ip, ports)

    return ports

def valid_config_value(key, value):
    # bool is a subclass of int, so rule it out explicitly for numeric options
    if key == "timeout":
        return isinstance(value, (int, float)) and not isinstance(value, bool) and value > 0
    if key == "max_worker":
        return isinstance(value, int) and not isinstance(value, bool) and value >= 1
    if key == "create_logs":
        return isinstance(value, bool)
    return False

def load_config():
    """
    Load the scanner config. A missing file, malformed JSON or an invalid
    value falls back to DEFAULT_CONFIG instead of crashing the scan.
    """
    config = dict(DEFAULT_CONFIG)

    path = (Path(__file__).resolve().parent.parent
                / "config"
                / "port_scanner_config.json")

    try:
        with open(path, 'r',encoding='utf-8') as file:
            user_config = json.load(file)
    except FileNotFoundError:
        return config
    except (OSError, ValueError) as e:
        print(f"Warning: could not read {path.name} ({e}). Using defaults.")
        return config

    if not isinstance(user_config, dict):
        print(f"Warning: {path.name} must contain a JSON object. Using defaults.")
        return config

    for key, value in user_config.items():
        if key not in DEFAULT_CONFIG:
            print(f"Warning: unknown config option '{key}' ignored.")
        elif valid_config_value(key, value):
            config[key] = value
        else:
            print(f"Warning: invalid value for '{key}' ({value!r}). "
                  f"Using default {DEFAULT_CONFIG[key]!r}.")

    return config
    
def create_logs(ip, ports):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = (Path(__file__).resolve().parent.parent
                / "logs"
                / f"port_scan_{ip}_{timestamp}.json")
    
    file_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(file_path, "w") as file:
        json.dump(ports, file, indent=4)

def parser():
    parser = argparse.ArgumentParser(description="Port Scanner")
    parser.add_argument("ip", nargs="?", type=str, help="Target hostname or IP.")
    parser.add_argument("-s", "--start", type=int, default=1, help="The starting port.")
    parser.add_argument("-e", "--end",  type=int, default=65535, help="The ending port.")

    return parser.parse_args()


def main(ip = None, start = None, end = None, timeout = None, workers = None, create_logs = None):

    if ip is None:
        args = parser()

        if args.ip is None:
            args.ip = input("Enter an ip address or hostname: ")
            args.start = int(input("Enter starting port: "))
            args.end = int(input("Enter ending port: "))
        
        ip = args.ip
        start = args.start
        end = args.end
    
    start_time = time.perf_counter()
    
    print("===================================")
    print("NetSpecter Port Scanner")
    print(f"Target: {ip}")
    print(f"Range: {start} - {end}")
    print("===================================")

    config = load_config()

    # Command-line options take priority over the config file
    overrides = {
        "timeout": ("--timeout", timeout),
        "max_worker": ("--workers", workers),
        "create_logs": ("--logs", create_logs)
    }

    for key, (flag, value) in overrides.items():
        if value is None:
            continue

        if not valid_config_value(key, value):
            print(f"Invalid value for {flag}: {value}")
            return

        config[key] = value

    try:
        ports = scan(
            config, 
            ip, 
            start, 
            end
        )

    except socket.gaierror as e:
        print(f"DNS resolution failed: {e}")
        return

    end_time = time.perf_counter()

    # scan() returns None when the port range is invalid
    if ports is not None:
        counter = len(ports)

        for port in ports:
            if port != None:
                print(f"{port['port']:<6}: Open   {port['latency']:>6.2f} ms   ({port['service']})")

        print("===================================")
        print("Scan Complete." + "\n" + f"{counter} open ports found.")
        print(f"Scan completed in {end_time - start_time:.2f} seconds")
        print("===================================")
    else:
        print("Scan not completed due to some unexpected error.")
        print("===================================")

if __name__ == "__main__":
    main()





    """
# Performance Notes

## Thread Pool Benchmark

NetSpecter uses Python's `ThreadPoolExecutor` to perform concurrent TCP port scanning.

During testing, different values of `max_workers` were evaluated to observe their effect on scan performance. Since port scanning is primarily an I/O-bound task, increasing the number of worker threads significantly reduced scan time up to a certain point.

### Test Environment

* Operating System: Arch Linux
* Python: 3.x
* Socket Timeout: 0.3 seconds

### Observations

* Approximately **1000 worker threads** provided good performance when scanning around **5,000 ports**.
* For larger scans (around **60,000 ports**), increasing the worker count to approximately **1600** further reduced total scan time on the test system.
* Increasing the worker count beyond these values produced little additional benefit and may increase CPU scheduling and memory overhead depending on the hardware.

**Note:** The optimal number of worker threads depends on the operating system, CPU, available memory, network latency, timeout values, and the number of ports being scanned. These values should be treated as experimental results rather than universal recommendations.

    """