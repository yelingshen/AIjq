"""Entrypoint used when building a Windows executable with PyInstaller.

This script exposes a simple CLI wrapper that invokes the package's
`multi_tool.cli:main` entrypoint. It's a thin shim to help PyInstaller
collect package resources and to have a stable single-file entry.
"""

import sys

if __name__ == '__main__':
    # Run the package CLI as a module would. Import lazily to allow PyInstaller
    # to discover package modules.
    from multi_tool.cli import main

    # Forward argv to the package CLI
    try:
        main()
    except SystemExit as e:
        # preserve exit codes
        raise
    except Exception as e:
        print(f"Fatal error launching multi_tool: {e}")
        sys.exit(2)
