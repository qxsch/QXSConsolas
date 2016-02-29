import re
import sys, os
import subprocess
from string import Template


class SSH:
    _command = []
    host = None
    stdin = None
    stdout = None
    stderr = None
    env = None

    def __init__(
        self,
        host = None,
        sshcommand = None,
        stdin = None,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE,
        env = None
    ):
        if sshcommand is None:
            sshcommand = [ "/usr/bin/ssh" ]
        self._command = sshcommand
        self.host   = host
        self.stdin  = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.env    = None

    def call(self, command):
        assert isinstance(command, list), "Please specify a command list"

        return call(
            quoteAsList(self._command + [ self.host, command ]),
            stdin  = self.stdin,
            stdout = self.stdout,
            stderr = self.stderr,
            env    = self.env,
            shell  = False
        )


def call(
    command,
    stdin = None,
    stdout = subprocess.PIPE,
    stderr = subprocess.PIPE,
    bufsize = 0,
    close_fds = False,
    cwd = None,
    env = None,
    shell = True,
    universal_newlines = False
):
    shell = bool(shell)
    if shell:
        executable = None
        args = quote(command)
    else:
        executable = command[0]
        #args = quote(command)
        args = quoteAsList(command)
    if env is None:
        env = os.environ
    if cwd is None:
        cwd = os.getcwd()

    p = subprocess.Popen(
        args = args,
        bufsize = bufsize,
        executable = executable,
        stdin = stdin,
        stdout = stdout,
        stderr = stderr,
        close_fds = close_fds,
        shell= shell,
        cwd = cwd,
        env = env,
        universal_newlines = universal_newlines
    )
    out, err = p.communicate()
    return [p.returncode, out, err]


def replaceVars(cmd, variables):
    newcmd = []
    for s in cmd:
        newcmd.append(Template(s).safe_substitute(variables))
    return newcmd

def quoteAsList(data):
    l = []
    if isinstance(data, list):
        for val in data:
            if isinstance(val, list):
                l.append(quote(val))
            else:
                l.append(str(val))
    else:
        l.append(str(data))
    return l


def quote(data, sub = False):
    if isinstance(data, list):
        data = " ".join([quote(val, True) for val in data])
        if not bool(sub):
            return data
    data=str(data)
    if quote.normalchars.match(data):
        return data
    else:
        return "'" + data.replace("'", "'\\''") + "'"

quote.normalchars = re.compile('^[a-zA-Z0-9_.-]+$')

