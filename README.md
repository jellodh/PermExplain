# perm-explain

Explains why you can or can't read, write or enter a path on Linux,
checking every directory on the way down.

## Usage

    python3 perm-explain.py PATH [r|w|x]
    python3 perm-explain.py --selftest

The letter defaults to `r` (read).

## Example

    $ python3 perm-explain.py /etc/shadow
    Can you read /etc/shadow?
      ok     /  mode 755, you count as other, need 'x'
      ok     /etc  mode 755, you count as other, need 'x'
      DENIED /etc/shadow  mode 640, you count as other, need 'r'
    -> No. Linux stops at /etc/shadow and never looks further down the path.

## How it works

Linux sorts you into one class for each file: owner, then group, then
other. The first match wins, and only that class's permission bits count.
Every directory on the path needs `x` (permission to pass through), and
the final file needs the bit you asked for.

## Limitations

- No ACLs, mount options (read-only, noexec), SELinux or AppArmor.
- It walks the path as written and does not resolve symlinks.
- As root, most checks are bypassed. The tool prints a note but can still
  report DENIED, so don't trust it as root.
- Checks the current user only. Linux only.

## License

MIT
