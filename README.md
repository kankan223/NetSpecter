# NetSpecter

NetSpecter is a Python-based collection of networking, system, and file management utilities developed as part of my cybersecurity and software engineering learning journey.

The project focuses on building practical command-line tools while learning networking concepts, concurrent programming, Linux development, and software architecture.

---

## Features

### Networking

* Multithreaded TCP Port Scanner
* DNS Resolution
* Service Detection
* Configurable Thread Pool
* Configurable Socket Timeout
* Port Scan JSON Logging
* Port Latency Measurement

### File Utilities

* Directory Analyzer
* File Organizer

### Security Utilities

* Cryptographically Secure Password Generator
* Optional Ambiguous Character Removal

### System Utilities

* System Information Viewer
* CPU Usage
* Memory Usage
* Disk Usage
* Network Statistics
* System Uptime

---

## Project Structure

```text
NetSpecter/
│
├── config/
│   └── port_scanner_config.json
│
├── logs/
│
├── scanner/
│   └── scanner.py
│
├── utilities/
│   ├── directory_analyzer.py
│   ├── file_organizer.py
│   ├── password_generator.py
│   └── system_monitor.py
│
├── README.md
├── LICENSE
├── requirements.txt
└── .gitignore
```

---

## Requirements

* Python 3.11+
* Linux (developed and tested on Arch Linux)

Python packages:

* psutil

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Usage

### Port Scanner

```bash
python scanner/scanner.py google.com

python scanner/scanner.py 192.168.1.1 -s 20 -e 1000
```

---

### Directory Analyzer

```bash
python utilities/directory_analyzer.py
```

---

### File Organizer

```bash
python utilities/file_organizer.py
```

---

### Password Generator

```bash
python utilities/password_generator.py
```

---

### System Information

```bash
python utilities/system_monitor.py
```

---

## Configuration

The port scanner reads its settings from:

```text
config/port_scanner_config.json
```

Current configurable options include:

* Socket timeout
* Maximum worker threads
* Log generation

---

## Output

The port scanner automatically saves scan results as JSON files inside the `logs/` directory.

The Directory Analyzer also generates both:

* Text reports
* JSON reports

---

## Future Improvements

Planned features include:

* Banner Grabbing
* UDP Port Scanner
* Network Discovery
* Rich Terminal Interface
* CLI Toolkit (`main.py`)
* Plugin Architecture
* Unit Tests
* PyQt GUI
* OS Fingerprinting

---

## Learning Goals

This project is being built to strengthen my understanding of:

* Python
* Networking
* Socket Programming
* Concurrent Programming
* Linux Development
* Cybersecurity Fundamentals
* Software Architecture
* Command-Line Applications
* Git and GitHub

---

## License

This project is licensed under the MIT License.

See the LICENSE file for details.
