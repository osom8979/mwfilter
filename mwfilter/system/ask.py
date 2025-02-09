# -*- coding: utf-8 -*-

from pathlib import Path


def ask_overwrite(file: Path, *, force_yes=False) -> bool:
    if not file.is_file():
        return True

    if force_yes:
        file.unlink()
        return True

    answer = input(f"Overwrite file '{str(file)}' (Y/n/s): ").strip().lower()
    if answer == "y":
        file.unlink()
        return True
    elif answer == "s":
        return False
    else:
        raise FileExistsError(f"Already exists file: '{str(file)}'")


def ask_continue(*, force_yes=False) -> bool:
    if force_yes:
        return True

    answer = input("Continue? (Y/n/s): ").strip().lower()
    if answer == "y":
        return True
    elif answer == "s":
        return False
    else:
        raise InterruptedError
