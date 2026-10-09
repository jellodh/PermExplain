#!/usr/bin/env python3
"""perm-explain: explain why you can or can't access a path."""
import os
import sys

NEED = {"r": 4, "w": 2, "x": 1}
WORDS = {"r": "read", "w": "write to", "x": "run or enter"}


def pick_class(file_uid, file_gid, my_uid, my_gids):
    """Return 'owner', 'group' or 'other'. First match wins."""
    if my_uid == file_uid:
        return "owner"
    if file_gid in my_gids:
        return "group"
    return "other"


def allowed(mode, who, letter):
    """Does this class's digit of the mode include the wanted bit?"""
    shift = {"owner": 6, "group": 3, "other": 0}[who]
    digit = (mode >> shift) & 7
    return bool(digit & NEED[letter])


def check_step(path, letter, uid, gids):
    """Check one path on the way. Returns True if allowed."""
    st = os.stat(path)
    who = pick_class(st.st_uid, st.st_gid, uid, gids)
    ok = allowed(st.st_mode, who, letter)
    mark = "ok    " if ok else "DENIED"
    print(f"  {mark} {path}  mode {st.st_mode & 0o777:03o}, you count as {who}, need '{letter}'")
    return ok


def selftest():
    assert pick_class(1000, 1000, 1000, {1000}) == "owner"
    assert pick_class(0, 1000, 1000, {1000}) == "group"
    assert pick_class(0, 50, 1000, {1000, 50}) == "group"
    assert pick_class(0, 50, 1000, {1000}) == "other"
    assert pick_class(1000, 50, 1000, {1000, 50}) == "owner"
    assert allowed(0o644, "owner", "w") and not allowed(0o644, "other", "w")
    print("all good")


def main():
    args = sys.argv[1:]
    if args == ["--selftest"]:
        selftest()
        return
    if not args or len(args) > 2:
        print("usage: perm-explain.py PATH [r|w|x]")
        sys.exit(1)
    letter = args[1] if len(args) == 2 else "r"
    if letter not in NEED:
        print("the letter must be r, w or x")
        sys.exit(1)

    target = os.path.abspath(args[0])
    uid = os.getuid()
    gids = set(os.getgroups()) | {os.getgid()}
    if uid == 0:
        print("note: you are root, which bypasses most of these checks")

    parts = [p for p in target.split("/") if p]
    if not parts:
        steps = [("/", letter)]
    else:
        steps = [("/", "x")]
        cur = ""
        for p in parts[:-1]:
            cur += "/" + p
            steps.append((cur, "x"))
        steps.append((target, letter))

    print(f"Can you {WORDS[letter]} {target}?")
    for path, need in steps:
        try:
            ok = check_step(path, need, uid, gids)
        except OSError as e:
            print(f"  ERROR  {path}: {e.strerror}")
            return
        if not ok:
            print(f"-> No. Linux stops at {path} and never looks further down the path.")
            return
    print("-> Yes. Every step on the way allows it.")


main()

