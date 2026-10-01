import argparse
import time

def build_parser():

    parser = argparse.ArgumentParser(
        prog = "NetSpecter",
        description = "Cybersecurity and System Utility Toolkit"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required = True
    )  

    # Scan TCP ports
    scan_parser = subparsers.add_parser(
        "scan",
        help = "Run the TCP port scanner"
    )

    scan_parser.add_argument(
        "ip",
        help = "Hostname or IP"
    )

    scan_parser.add_argument(
        "-s",
        "--start",
        type = int,
        default = 1,
        help="The starting port."
    )

    scan_parser.add_argument(
        "-e",
        "--end", 
        type=int,
        default=65535,
        help="The ending port."
    )

    scan_parser.add_argument(
        "-t",
        "--timeout",
        type = float,
        help = "Socket timeout in seconds (overrides config)"
    )

    scan_parser.add_argument(
        "-w",
        "--workers",
        type = int,
        help = "Maximum worker threads (overrides config)"
    )

    scan_parser.add_argument(
        "--logs",
        action = argparse.BooleanOptionalAction,
        help = "Save a JSON scan report (overrides config)"
    )

    # Display system information
    system_parser = subparsers.add_parser(
        "system",
        help = "Display system information"
    )

    # Generate passwords
    password_parser = subparsers.add_parser(
        "password",
        help = "Generate passwords"
    )

    password_parser.add_argument(
        "-l",
        "--length",
        type = int,
        default=16,
        help = "Length of the generated password"
    )

    password_parser.add_argument(
        "-a",
        "--ambiguous",
        action = 'store_true',
        help = "Use to exclude ambiguous characters"
    )

    # Analyze directories
    analyze_parser = subparsers.add_parser(
        "analyze",
        help = "Analyze a directory and generate reports"
    )

    analyze_parser.add_argument(
        "path",
        type = str
    )


    # Organize files
    organize_parser = subparsers.add_parser(
        "organize",
        help = "Automatically organize files into folders"
    )

    organize_parser.add_argument(
        "path",
        type = str
    )

    organize_mode = organize_parser.add_mutually_exclusive_group()

    organize_mode.add_argument(
        "--dry-run",
        action = 'store_true',
        help = "Show what would be moved without moving anything"
    )

    organize_mode.add_argument(
        "--undo",
        action = 'store_true',
        help = "Reverse the most recent organize of this folder"
    )


    return parser


def main():
        
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "system":
        from utils import system_monitor

        system_monitor.main()

    elif args.command == "scan":
        from scanner import port_scanner

        port_scanner.main(
            ip = args.ip,
            start = args.start,
            end = args.end,
            timeout = args.timeout,
            workers = args.workers,
            create_logs = args.logs
        )

    elif args.command == "password":
        from utils import password_generator

        password_generator.main(
            length = args.length,
            exclude_ambiguous = args.ambiguous
        )

    elif args.command == "analyze":
        from utils import directory_analyzer
        directory_analyzer.main(path = args.path)

    elif args.command == "organize":
        from utils import file_organizer
        file_organizer.main(
            path = args.path,
            dry_run = args.dry_run,
            undo_last = args.undo
        )

if __name__ == "__main__":
    main()