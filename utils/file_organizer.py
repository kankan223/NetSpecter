from pathlib import Path
from datetime import datetime
import json
import shutil

# Every real organize run records its moves here so it can be undone
LOGS_DIR = Path(__file__).resolve().parent.parent / "logs"


def organizer(path, dry_run = False):
    """
    Move the files in `path` into category folders.

    Returns (moves, failed, manifest_path). With dry_run, nothing is moved
    or created: `moves` is the plan and manifest_path is None.
    """
    folders = {
        "Images":(
            ".png",
            ".jpg",
            ".jpeg"
        ),
        "PDFs":(
            ".pdf",
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
            ".txt",
            ".md"
        ),
        "Archives":(
            ".zip",
            ".rar",
            ".7z"
        )
    }

    moves = []
    failed = []
    created_dirs = []
    planned = set()
    manifest_path = None

    try:
        # Take the listing up front: the loop creates folders inside this directory
        for item in sorted(path.iterdir()):
            if not item.is_file():
                continue

            destination = "others"

            for folder, extentions in folders.items():
                if item.suffix.lower() in extentions:
                    destination = folder
                    break

            new_path = path / destination
            destination_path = new_path / item.name

            counter = 1

            # `planned` catches name clashes in a dry run, where nothing exists yet
            while destination_path.exists() or destination_path in planned:
                destination_path = (
                    new_path /
                    f"{item.stem}_{counter}{item.suffix}"
                )
                counter += 1

            planned.add(destination_path)

            if dry_run:
                moves.append((item, destination_path))
                continue

            try:
                if not new_path.exists():
                    new_path.mkdir()
                    created_dirs.append(new_path)

                shutil.move(item, destination_path)
                moves.append((item, destination_path))
            except OSError as e:
                failed.append((item, e))

    finally:
        # Written even if the run is interrupted, so completed moves can still be undone
        if not dry_run and moves:
            manifest_path = write_manifest(path, moves, created_dirs)

    return moves, failed, manifest_path


def write_manifest(path, moves, created_dirs):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    manifest_path = LOGS_DIR / f"organize_{timestamp}.json"

    LOGS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    data = {
        "path": str(path),
        "moves": [[str(source), str(destination)] for source, destination in moves],
        "created_dirs": [str(folder) for folder in created_dirs]
    }

    with open(manifest_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

    return manifest_path


def find_latest_manifest(path):
    # Timestamps in the file names sort chronologically
    for manifest_path in sorted(LOGS_DIR.glob("organize_*.json"), reverse=True):
        try:
            with open(manifest_path, "r", encoding="utf-8") as file:
                data = json.load(file)
        except (OSError, ValueError):
            continue

        if data.get("path") == str(path):
            return manifest_path, data

    return None, None


def undo(path):
    """
    Reverse the most recent organize of `path`.

    Returns (restored, skipped), or None if there is nothing to undo.
    Files that were moved or replaced since are skipped, never overwritten.
    """
    manifest_path, data = find_latest_manifest(path)

    if manifest_path is None:
        return None

    restored = 0
    skipped = []

    for source, destination in reversed(data["moves"]):
        source = Path(source)
        destination = Path(destination)

        if not destination.exists():
            skipped.append((destination, "no longer exists"))
            continue

        if source.exists():
            skipped.append((source, "a file with this name already exists"))
            continue

        try:
            shutil.move(destination, source)
            restored += 1
        except OSError as e:
            skipped.append((destination, e))

    # Remove the folders the organize run created, but only if they are now empty
    for folder in data["created_dirs"]:
        try:
            Path(folder).rmdir()
        except OSError:
            pass

    # Keep the record, but take it out of the undo history
    manifest_path.rename(manifest_path.with_name("undone_" + manifest_path.name))

    return restored, skipped


def main(path = None, dry_run = False, undo_last = False):

    print("==================================")
    print("\n" + "---------FOLDER ORGANIZER---------")
    print("==================================")

    if path == None:
        path = input("Enter a folder path : \n")

    try:
        path = Path(path).resolve()

        if not path.exists():
            raise FileNotFoundError
        
        if not path.is_dir():
            raise NotADirectoryError

        if undo_last:
            result = undo(path)

            if result is None:
                print("\n" + f"No organize history found for {path}.")
            else:
                restored, skipped = result
                print("\n" + f"Restored {restored} files in {path}.")

                for item, reason in skipped:
                    print(f"Skipped {item}: {reason}")

            print("\n" + "==================================")
            return

        moves, failed, manifest_path = organizer(path, dry_run)

        if not moves and not failed:
            print("\n" + "No files to organize.")
        elif dry_run:
            print()
            for source, destination in moves:
                print(f"{source.name}  ->  {destination.relative_to(path)}")

            print("\n" + f"Dry run: {len(moves)} files would be moved. Nothing was changed.")
        else:
            print("\n" + f"The folder {path} has been organized. {len(moves)} files moved.")

            for item, error in failed:
                print(f"Could not move {item.name}: {error}")

            if manifest_path is not None:
                print(f"Undo with: python main.py organize \"{path}\" --undo")

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
