from pathlib import Path
from datetime import datetime
import json
import os

# Keys in the report that are not file extensions
SUMMARY_KEYS = ("file", "folder", "dir_size", "skipped")

def report(path):

    """
    Analyze a directory recursively.

    Returns a dictionary containing:
    - Total files
    - Total folders
    - Counts of supported file extensions

    Unknown extensions are counted under 'others'. Symlinks are not followed
    or counted. Anything that could not be read is listed under 'skipped'.
    """

    file_types = {
        "file": 0,
        "folder": 0, 
        ".py": 0,   
        ".pdf": 0,
        ".png": 0,
        ".txt": 0,
        ".mp4": 0,
        ".mp3": 0,
        ".md": 0,  
        ".docx": 0,    
        ".jpg": 0,
        ".jpeg": 0,     
        ".csv": 0,    
        ".mov": 0,    
        ".exe": 0,  
        ".zip": 0,  
        "others": 0,   
        "dir_size": 0,
        "skipped": []
    }

    # os.walk reports unreadable folders through onerror, where rglob skips them silently
    def on_error(error):
        file_types["skipped"].append(str(error.filename))

    for root, dirs, files in os.walk(path, onerror=on_error):
        root = Path(root)

        for name in dirs:
            if not (root / name).is_symlink():
                file_types["folder"] += 1

        for name in files:
            item = root / name

            try:
                if item.is_symlink() or not item.is_file():
                    continue

                size = item.stat().st_size
            except OSError:
                # e.g. deleted while the walk was running
                file_types["skipped"].append(str(item))
                continue

            file_types["file"] += 1
            file_types["dir_size"] += size

            suffix = item.suffix.lower()
            if suffix in file_types:
                file_types[suffix] += 1
            else:
                file_types["others"] += 1

    return file_types

def write_report(path, data):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    log_file_path = (Path(__file__).resolve().parent.parent
                     / "logs"
                     / f"directory_report_{timestamp}.txt")
    
    log_file_path_json = (Path(__file__).resolve().parent.parent
                     / "logs"
                     / f"directory_report_{timestamp}.json")

    report = [
        "Folder Analysis Report",
        "======================",
        "",
        f"Path: {path}",
        f"Files : {data['file']}",
        f"Folders : {data['folder']}",
        "",
        "Extensions:"
    ]

    log_file_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(log_file_path_json, "w") as f:
        json.dump(data, f, indent = 4)

    with open(log_file_path, "w", encoding="utf-8") as file:
        file.write("\n".join(report))

        for key, value in data.items():
            if key not in SUMMARY_KEYS and value > 0:
                file.write("\n" + f"{key} : {value}")

        file.write("\n\n" + f"Folder Size : {format_size(data['dir_size'])}")

        if data["skipped"]:
            file.write("\n\n" + f"Skipped (could not be read) : {len(data['skipped'])}")

            for item in data["skipped"]:
                file.write("\n" + item)
    return log_file_path, log_file_path_json

    
# def get_dir_size(path):
#     return sum(f.stat().st_size for f in Path(path).rglob('*') if f.is_file())

def format_size(size_in_bytes):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_in_bytes < 1024.0:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024.0
    return f"{size_in_bytes:.2f} PB"

def main(path = None):

    print("==================================")
    print("\n" + "---------FOLDER  ANALYZER---------")
    print("==================================")

    if path == None:
        path = input("Enter a folder path : \n")

    try:
        path = Path(path)

        if not path.exists():
            raise FileNotFoundError
        
        if not path.is_dir():
            raise NotADirectoryError
        
        data = report(path) 

        print("Folder Analysis Report")
        print("======================")
        print("\n" + f"Path: {path}")
        print(f"Files : {data['file']}")
        print(f"Folders : {data['folder']}")
        print("\n" + "Extensions:")

        for key, value in data.items():
            if key not in SUMMARY_KEYS and value > 0:
                print(f"{key} : {value}")

        print("\n" + f"Folder Size : {format_size(data['dir_size'])}")

        if data["skipped"]:
            print("\n" + f"Warning: {len(data['skipped'])} items could not be read, so totals may be incomplete:")

            for item in data["skipped"][:5]:
                print(f"  {item}")

            if len(data["skipped"]) > 5:
                print("  ... full list in the report files")

        txt_path, json_path = write_report(path, data)
        print(f"TXT report saved to: {txt_path}")
        print(f"JSON report saved to: {json_path}")

    except FileNotFoundError:
        print("Folder does not exist. Check the path.")
        return
    except PermissionError:
        print("Permission denied. You don't have permission to open this folder")
        return
    except NotADirectoryError:
        print("The provided path is not a directory.")
        return
    except Exception as e:
        print(f"Unexpected error: {e}")
        return

    print("\n" + "==================================")
             

if __name__ == "__main__":
    main()