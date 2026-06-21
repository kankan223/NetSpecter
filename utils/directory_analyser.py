from pathlib import Path
from datetime import datetime
import json
from collections import defaultdict

def report(path):

    """
    Analyze a directory recursively.

    Returns a dictionary containing:
    - Total files
    - Total folders
    - Counts of supported file extensions

    Unknown extensions are counted under 'others'.
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
        "dir_size": 0       
    }


    for item in path.rglob("*"):
        if item.is_file():
            file_types["file"] += 1
            file_types["dir_size"] += item.stat().st_size
            
            suffix = item.suffix.lower()
            if suffix in file_types:
                file_types[suffix] += 1
            else:
                file_types["others"] += 1

        elif item.is_dir():
            file_types["folder"] += 1

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
            if key not in ("file", "folder", "dir_size") and value > 0:
                file.write("\n" + f"{key} : {value}")

        file.write("\n\n" + f"Folder Size : {format_size(data['dir_size'])}")
    return log_file_path, log_file_path_json

    
# def get_dir_size(path):
#     return sum(f.stat().st_size for f in Path(path).rglob('*') if f.is_file())

def format_size(size_in_bytes):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_in_bytes < 1024.0:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024.0

def main():
    dir_path = input("Enter a folder path : \n")

    try:
        path = Path(dir_path)

        if not path.exists():
            raise FileNotFoundError
        
        if not path.is_dir():
            raise NotADirectoryError
        
        data = report(path) 

        print("Folder Analysis Report")
        print("======================")
        print("\n" + f"Path: {dir_path}")
        print(f"Files : {data['file']}")
        print(f"Folders : {data['folder']}")
        print("\n" + "Extensions:")

        for key, value in data.items():
            if key not in ("file", "folder", "dir_size") and value > 0:
                print(f"{key} : {value}")

        print("\n" + f"Folder Size : {format_size(data['dir_size'])}")

        txt_path, json_path = write_report(dir_path, data)
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
         
    
    

if __name__ == "__main__":
    main()