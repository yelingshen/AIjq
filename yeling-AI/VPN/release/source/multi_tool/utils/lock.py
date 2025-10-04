"""FileLock: small reliable file lock used by the orchestrator.

This module provides a minimal FileLock context manager. On POSIX it uses
fcntl.flock on a <path>.lock file. On other platforms it falls back to
creating and removing a sentinel directory.
"""

import os
import time
import errno


class FileLock:
    """Exclusive file lock context manager.

    Usage:
        with FileLock('/tmp/mylock', timeout=10):
            # critical section
    """

    def __init__(self, path: str, timeout: int = 10):
        self.path = path
        self.timeout = timeout
        self._fp = None
        self._is_posix = os.name == 'posix'

    def acquire(self) -> None:
        start = time.time()
        if self._is_posix:
            import fcntl

            lockfile = self.path if self.path.endswith('.lock') else self.path + '.lock'
            self._fp = open(lockfile, 'w')
            while True:
                try:
                    fcntl.flock(self._fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    return
                except OSError as e:
                    if e.errno not in (errno.EACCES, errno.EAGAIN):
                        try:
                            self._fp.close()
                        except Exception:
                            pass
                        self._fp = None
                        raise
                if time.time() - start > self.timeout:
                    try:
                        self._fp.close()
                    except Exception:
                        pass
                    self._fp = None
                    raise TimeoutError(f"Timeout acquiring lock {lockfile}")
                time.sleep(0.05)
        else:
            while True:
                try:
                    os.mkdir(self.path)
                    return
                except FileExistsError:
                    if time.time() - start > self.timeout:
                        raise TimeoutError(f"Timeout acquiring lock {self.path}")
                    time.sleep(0.05)

    def release(self) -> None:
        if self._is_posix:
            try:
                import fcntl
                if self._fp:
                    try:
                        fcntl.flock(self._fp, fcntl.LOCK_UN)
                    except Exception:
                        pass
                    try:
                        self._fp.close()
                    except Exception:
                        pass
                    self._fp = None
            except Exception:
                self._fp = None
        else:
            try:
                if os.path.isdir(self.path):
                    os.rmdir(self.path)
            except Exception:
                pass

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.release()

