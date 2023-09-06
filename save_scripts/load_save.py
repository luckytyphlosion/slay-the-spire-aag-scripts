import sys
import argparse
import os
import shutil
import glob

GAME_SAVES_DIRECTORY = "/mnt/c/Program Files (x86)/Steam/steamapps/common/SlayTheSpire/preferences"
DEFAULT_SAVE_SLOT = "2"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("save_id")
    ap.add_argument("save_slot", nargs="?", default=DEFAULT_SAVE_SLOT)

    args = ap.parse_args()

    save_id = args.save_id
    save_slot = args.save_slot
    if save_slot in {"0", ""}:
        if save_slot == "":
            save_slot = "0"

        is_slot_0 = True
        save_slot_prefix = "[!12]"
    elif save_slot in {"1", "2"}:
        is_slot_0 = False
        save_slot_prefix = f"{save_slot}_"
    else:
        print(f"Invalid save slot! (Must be 0, 1, 2, or \"\")")
        sys.exit(1)

    cur_directories = next(os.walk('.'))[1]
    found_directory = None

    for cur_directory in cur_directories:
        if cur_directory.split("_", maxsplit=1)[0] == save_id:
            found_directory = cur_directory
            break

    if found_directory is None:
        print(f"Save id {save_id} does not exist!")
        sys.exit(1)

    for old_save_file in glob.glob(f"{GAME_SAVES_DIRECTORY}/{save_slot_prefix}*"):
        os.remove(old_save_file)

    saved_save_dirname, saved_save_dirnames, saved_save_filenames = next(os.walk(found_directory))
    invalid_save_files = []

    for saved_save_filename in saved_save_filenames:
        if is_slot_0:
            is_correct_slot = saved_save_filename[0] not in {"1", "2"} and saved_save_filename[1] != "_"
        else:
            is_correct_slot = saved_save_filename.startswith(save_slot_prefix)

        if not is_correct_slot:
            invalid_save_files.append(saved_save_filename)

    if len(invalid_save_files) != 0:
        invalid_save_files_error_message = f"Error: The saved save {found_directory} contains save files not part of the save slot {save_slot}:\n"
        invalid_save_files_error_message += "".join(f"- {invalid_save_file}\n" for invalid_save_file in invalid_save_files)
        print(invalid_save_files_error_message)
        sys.exit(1)

    for saved_save_filename in saved_save_filenames:
        shutil.copyfile(f"{saved_save_dirname}/{saved_save_filename}", f"{GAME_SAVES_DIRECTORY}/{saved_save_filename}")

    print(f"Copied saved save {found_directory} to saves!")

if __name__ == "__main__":
    main()
