from pathlib import Path
import shutil


def organizer(path):
    folders = {
        "Images":(
            ".png",
            ".jpg",
            ".jpeg"
        ),
        "PDFs":(
            ".pdf"
        ),
        "Videos":(
            ".mp4",
            ".mkv"
        ),
        "Audio":(
            ".mp3",
            ".wav",
        ),
        "Code":(
            ".py",
            ".cpp",
            ".c",
            ".php"
        ),
        "Documents":(
            ".docx",
            "txt",
            ".md"
        ),
        "Archives":(
            ".zip",
            ".rar",
            ".7z"
        )
    }

    for item in path.iterdir():
        if item.is_file():
            destination = "others"

            for folder, extentions in folders.items():
                if item.suffix.lower() in extentions:
                    destination = folder
                    break
            
            new_path =Path(path) / destination
            new_path.mkdir(exist_ok=True)

            destination_path = new_path / item.name

            counter = 1

            while destination_path.exists():
                destination_path = (
                    new_path /
                    f"{item.stem}_{counter}{item.suffix}"
                )
                counter += 1

            shutil.move(item, destination_path)
            
    
def main(path = None):

    print("==================================")
    print("\n" + "---------FOLDER ORGANIZER---------")
    print("==================================")

    if path == None:
        path = input("Enter a folder path : \n")

    try:
        path = Path(path)

        if not path.exists():
            raise FileNotFoundError
        
        if not path.is_dir():
            raise NotADirectoryError
        

        organizer(path)

        print("\n" + f"The folder {path} has been organized.")
        print("\n" + "==================================")

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