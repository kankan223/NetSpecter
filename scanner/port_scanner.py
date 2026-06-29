import socket
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from pathlib import Path
from datetime import datetime
import argparse

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
    with socket.socket() as s:
        s.settimeout(timeout)

        latency_start_time = time.perf_counter()
        result = s.connect_ex((ip, port))
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

            latency_end_time = time.perf_counter()
            return {"port": port,
                    "service": service,
                    "latency": (latency_end_time - latency_start_time) * 1000}


def scan(config, ip, start, end):
    # if validate_port(start, end):
    #     start = int(start)
    #     end = int(end)
    
    if not validate_range(start, end):
        return None
    
    ip = socket.gethostbyname(ip)

    with ThreadPoolExecutor(max_workers=min(config['max_worker'], end - start + 1)) as executor:
        futures = [executor.submit(scan_port, config['timeout'], ip, port) for port in range(start, end + 1)]
        data = [f.result() for f in futures]
    
    ports = [port for port in data if port is not None]

    if config['create_logs']:
        create_logs(ip, ports)

    return ports

def load_config():
    path = (Path(__file__).resolve().parent.parent
                / "config"
                / "port_scanner_config.json")
    
    with open(path, 'r',encoding='utf-8') as file:
        return json.load(file)
    
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


def main(ip = None, start = None, end = None):

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
    counter = len(ports)
    
    if ports != None:
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