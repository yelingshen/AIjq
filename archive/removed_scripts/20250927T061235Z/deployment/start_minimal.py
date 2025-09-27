#!/usr/bin/env python3
"""Wrapper to start the minimal Flask server (ai/server_minimal.py)."""
import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AI_DIR = ROOT / 'ai'
sys.path.insert(0, str(AI_DIR))

if __name__ == '__main__':
    print('[deployment] Starting minimal server (ai/server_minimal.py)')
    runpy.run_path(str(AI_DIR / 'server_minimal.py'), run_name='__main__')
#!/usr/bin/env python3
#"""Wrapper to start the minimal Flask server (ai/server_minimal.py)."""
#import runpy
#import sys
#from pathlib import Path
#
#ROOT = Path(__file__).resolve().parent.parent
#AI_DIR = ROOT / 'ai'
#sys.path.insert(0, str(AI_DIR))
#
#if __name__ == '__main__':
#    print('[deployment] Starting minimal server (ai/server_minimal.py)')
#    runpy.run_path(str(AI_DIR / 'server_minimal.py'), run_name='__main__')
#!/usr/bin/env python3
"""Wrapper to start the minimal Flask server (ai/server_minimal.py)."""
import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AI_DIR = ROOT / 'ai'
sys.path.insert(0, str(AI_DIR))

if __name__ == '__main__':
    print('[deployment] Starting minimal server (ai/server_minimal.py)')
    runpy.run_path(str(AI_DIR / 'server_minimal.py'), run_name='__main__')
