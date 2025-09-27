"""Shim to keep root auto_deploy.py working while main implementation lives in scripts/"""
import runpy
import os

THIS_DIR = os.path.dirname(__file__)
TARGET = os.path.normpath(os.path.join(THIS_DIR, '..', 'auto_deploy.py'))

if __name__ == '__main__':
    runpy.run_path(TARGET, run_name='__main__')
