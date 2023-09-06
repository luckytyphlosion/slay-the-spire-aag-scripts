import sys
import argparse
import os
import shutil
import glob
import pathlib

GAME_SAVES_DIRECTORY = "/mnt/c/Program Files (x86)/Steam/steamapps/common/SlayTheSpire/preferences"
DEFAULT_SAVE_SLOT = "2"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("save_id")
    ap.add_argument("save_name")
    ap.add_argument("save_slot", nargs="?", default=DEFAULT_SAVE_SLOT)
    ap.add_argument("-f", "--overwrite", dest="overwrite", action="store_true", default=False)

    args = ap.parse_args()

    save_id = args.save_id
    save_name = args.save_name
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

    cur_saved_save_directories = next(os.walk('.'))[1]
    saved_save_directories_with_given_save_id = []

    for cur_saved_save_directory in cur_saved_save_directories:
        if cur_saved_save_directory.split("_", maxsplit=1)[0] == save_id:
            saved_save_directories_with_given_save_id.append(cur_saved_save_directory)

    if (len(saved_save_directories_with_given_save_id) > 1) or (len(saved_save_directories_with_given_save_id) == 1 and not args.overwrite):
        print(f"Error: multiple saves with the same id {save_id} (listed below)\n" + "".join(f"- {saved_save_directory_with_given_save_id}\n" for saved_save_directory_with_given_save_id in saved_save_directories_with_given_save_id))
        sys.exit(1)
    elif len(saved_save_directories_with_given_save_id) == 1 and args.overwrite:
        existing_saved_save_directory = saved_save_directories_with_given_save_id[0]
        print(f"Overwriting previous save {existing_saved_save_directory}!")
        shutil.rmtree(existing_saved_save_directory)

    saved_save_directory = f"{save_id}_{save_name}"
    pathlib.Path(saved_save_directory).mkdir()

    for save_filename in glob.glob(f"{GAME_SAVES_DIRECTORY}/{save_slot_prefix}*"):
        save_basename = pathlib.Path(save_filename).name
        shutil.copyfile(save_filename, f"{saved_save_directory}/{save_basename}")

    print(f"Created saved save for slot {save_slot} at {saved_save_directory}!")

if __name__ == "__main__":
    main()
