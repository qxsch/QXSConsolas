import os, shutil, tempfile


class TmpDir:
    _tmpdir = None
    def __init__(self, suffix='', prefix='tmp', directory=None):
        self._suffix = suffix
        self._prefix = prefix
        self._dir = directory
    def __enter__(self):
        if not (self._tmpdir is None):
            raise TmpException("A tmp directory has already been set up")
        self._tmpdir = tempfile.mkdtemp(self._suffix, self._prefix, self._dir)
        return self._tmpdir
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._tmpdir is None:
            raise TmpException("No tmp directory has been set up")
        shutil.rmtree(self._tmpdir)
        self._tmpdir = None

def CreateTmpDir(suffix='', prefix='tmp', directory=None):
    return TmpDir(suffix, prefix, directory)

def CreateTmpFIle(mode='w+b', bufsize=-1, suffix='', prefix='tmp', directory=None):
    return tempfile.TemporaryFile(mode, bufsize, suffix, prefix, directory)

