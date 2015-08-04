
def lookup_command(cmd, context):
    if (cmd in Proc.commands):
        return Proc(Proc.commands[cmd], context)
    else:
        return ShellProc(cmd, context)

class ShellContext(object):

    def __init__(self, cwd):
        self._cwd = cwd
        self._cmd = Proc('', self)

    def execute(self, cmd):
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
        "exit": "exit"
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
        return self._command

    def __repr__(self):
        return self.value

    def start():
        self._running = True
        pass

    def abort():
        self._running = False
        pass


class ShellProc(Proc):
    def kill(self):
        self.abort()

