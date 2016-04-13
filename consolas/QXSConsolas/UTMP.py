import struct
import sys, os

class UTMP:
    def __init__(self, utmpFile = '/var/run/utmp', wtmpFile = '/var/log/wtmp'):
        self._struct = 'hi32s4s32s256shhiii4i20x'
        self._structSize = struct.calcsize(self._struct)
        self._utmpFile = utmpFile
        self._wtmpFile = wtmpFile

    def read(self, filename):
        result = []
        with open(filename, 'rb') as fp:
            while True:
                bytes = fp.read(self._structSize)
                if not bytes:
                    break
                data = struct.unpack(self._struct, bytes)
                data = [(lambda s: str(s).split("\0", 1)[0])(i) for i in data]
                if data[0] != '0':
                    result.append(data)
        result.reverse()
        return result

    def readUtmp(self):
        return self.read(self._utmpFile)
    def readWtmp(self):
        return self.read(self._wtmpFile)

    def getRealUser(self):
        ttyname = os.ttyname(sys.stdout.fileno())
        for entry in self.readUtmp():
            if entry[4] == "":
                continue
            if ttyname.endswith(entry[2]):
                return entry[4]

