import os, socket, subprocess, shlex
from contextlib import contextmanager
from scap.utils import sudo_check_call
context_stack = []

@contextmanager
def ShellContextManager():
    if len(context_stack) > 0:
        parent = context_stack[-1]
    else:
        parent = None

    shell_context = ShellContext(parent)
    context_stack.append(shell_context)
    try:
        yield shell_context
    finally:
        context_stack.pop()

def execute(cmd):
    print('execute %s' % cmd)
    return context_stack[-1].execute(cmd)

class ShellCommandToken(object):
    def __init__(self, token, text):
        self._token = token
        self._text = text

    @property
    def token(self):
        return self._token

    @property
    def text(self):
        return self._text

    def __repr__(self):
        return self._text


def interpret_command(cmd, context):
    tokens = shlex.split(cmd)
    return tokens

def lookup_command(tokens, context):
    if (tokens[0] in Proc.commands):
        return Proc(tokens, context)
    else:
        proc = ShellProc(tokens, context)
        return proc

class ShellContext(object):
    def __init__(self, parent=None, cwd=os.getcwd()):
        self._parent = parent
        self._cwd = cwd
        self._cmd = Proc([], self)
        self.h = socket.gethostname()
        self.u = os.environ['LOGNAME']

    def execute(self, cmd):
        cmd = interpret_command(cmd, self)
        if cmd[0] == 'cd' and len(cmd) > 1:
            os.chdir(cmd[1])
            if not self._cwd == os.getcwd():
                self._cwd = os.getcwd()
            else:
                print("Directory '%s' doesn't exist." % cmd[1])
            self._cmd = Proc(cmd,self)
        else:
            self._cmd = lookup_command(cmd, self)

        return self._cmd

    @property
    def cmd(self):
        return self._cmd

    @property
    def cwd(self):
        return self._cwd
    @cwd.setter
    def cwd(self, cwd):
        self._cwd=cwd

    def __getitem__(self, key):
        return getattr(self, key)

class Proc(object):
    commands = {
        "exit": "exit",
        "detach": "detach"
    }
    def __init__(self, command, context):
        self._command=command
        self._context=context
        self._running=False

    @property
    def running(self):
        return self._running

    @property
    def value(self):
        return " ".join(self._command)

    def __repr__(self):
        return self.value

    def start(self):
        self._running = True
        pass

    def abort(self):
        self._running = False
        pass


class ShellProc(Proc):
    def kill(self):
        self.abort()

    def start(self):
        self._running = True
        output = sudo_check_call('root', self.value)
        print(output)
        #self._process = subprocess.Popen(self.value, shell=True)
        #self._running = True
