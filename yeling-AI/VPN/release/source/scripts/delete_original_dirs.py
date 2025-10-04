#!/usr/bin/env python3
import shutil, os, sys

BASE = r"C:\Users\WJ\Desktop\VPN"
DIRS = [
    os.path.join(BASE, 'ubuntu_file_helper_gui'),
    os.path.join(BASE, 'yeling_super_helper_tui'),
    os.path.join(BASE, 'yl'),
]

def main():
    for d in DIRS:
        try:
            if os.path.exists(d):
                shutil.rmtree(d)
                print(f'Removed: {d}')
            else:
                print(f'Not found: {d}')
        except Exception as e:
            print(f'Failed to remove {d}: {e}')

    # list parent
    try:
        print('\nParent directory contents:')
        for n in sorted(os.listdir(BASE)):
            print(' -', n)
    except Exception as e:
        print('Failed listing parent dir:', e)

if __name__ == '__main__':
    main()
