import os
import socket
import subprocess
import shlex
import sys
from contextlib import contextmanager
from scap.project import ScapProject
from mozprocess import processhandler

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


class ShellContext(object):
    def __init__(self, parent=None, cwd=os.getcwd()):
        self._parent = parent
        self._cwd = cwd
        self._cmd = Proc([], self)
        self.h = socket.gethostname()
        self.u = os.environ['LOGNAME']
        self._project = ScapProject()
        self._commands = None

    def execute(self, cmd):
        cmd = shlex.split(cmd)
        if cmd[0] == 'cd' and len(cmd) > 1:
            os.chdir(cmd[1])
            if not self._cwd == os.getcwd():
                self._cwd = os.getcwd()
            else:
                print("Directory '%s' doesn't exist." % cmd[1])
            self._cmd = Proc(cmd,self)
        else:
            self._cmd = self.lookup_command(cmd)

        return self._cmd

    def lookup_command(self, tokens):
        if (tokens[0] in Proc.commands):
            return Proc(tokens, self)
        else:
            try:
                proc = ProjectCommand(tokens, self)
            except Exception as ex:
                print ex
                proc = ShellProc(tokens, self)

            return proc

    @property
    def project(self):
        return self._project

    @property
    def project_name(self):
        return self._project.project_name

    @property
    def project_root(self):
        return self._project.project_root

    @property
    def cmd(self):
        return self._cmd

    @property
    def cwd(self):
        return self._cwd

    @property
    def rcwd(self):
        ''' The current working directory, relative to the project root '''
        relpath = self._cwd.replace(self.project_root, '')
        if relpath == '':
            relpath = '/'
        return relpath

    @cwd.setter
    def cwd(self, cwd):
        self._cwd = cwd

    @property
    def commands(self):
        if self._commands is None:
            cmds = {}
            if os.path.exists(self._project.command_path):
                for filename in os.listdir(self._project.command_path):
                    if filename.endswith('.py'):
                        cmd_name = os.path.basename(filename)
                        cmd_name = cmd_name[:-3]
                        cmds[cmd_name] = ProjectCommand([cmd_name], self)
            self._commands = cmds
        return self._commands

    def __getitem__(self, key):
        return getattr(self, key)


class Proc(object):
    commands = {
        "exit": "exit",
        "detach": "detach"
    }

    def __init__(self, command, context):
        self._command = command
        self._context = context
        self._running = False

    @property
    def running(self):
        return self._running

    @property
    def value(self):
        return " ".join(self._command)

    def args(self):
        return self._command

    def __repr__(self):
        return self.value

    def __len__(self):
        return self._command.__len__()

    def __getitem__(self, key):
        return self._command.__getitem__(key)

    def __setitem__(self, key, value):
        return self._command.__setitem__(key, value)

    def start(self):
        self._running = True

    def abort(self):
        self._running = False
        pass


class ProjectCommand(Proc):
    '''
    Project-level commands are implemented in python modules which get
    dynamically loaded from project_root/scap/cmds/*.py

    The command name is the module's file name. The command entrypoint is
    the 'run' method within the command module. To add subcommands to a
    command module simply simply add functions that follow the following
    naming convention:

    Any function that starts with run_ followed by the name of the sub
    command defines a callable sub command under the top-level command that
    is defined in that same module. For example:

        `run_{subcommand}(*args)` - adds a sub command named "subcommand"
    '''

    def __init__(self, command, context):
        self.subcommands = []
        self._context = context
        self._running = False
        cmd_module = __import__("cmds.%s" % command[0], fromlist=["cmds"])

        if len(command) > 1 and hasattr(cmd_module, command[1]):
            command = command[1:]
            self._run = getattr(cmd_module, command[0])
        elif hasattr(cmd_module, 'run'):
            self._run = cmd_module.run
            for i in dir(cmd_module):
                if i.startswith('run_'):
                    self.subcommands.append(i[4:])
        else:
            self._run = None
        self._command = command

    def start(self):
        self._running = True
        if self._run is not None:
            args = self._command[1:]
            self._run(*args)
        self._running = False


class ShellProc(Proc):
    def kill(self):
        self.abort()

    def start(self):

        if hasattr(self._context, 'output_tty'):
            output_tty = open(self._context.output_tty, 'w')
            close_tty = True
        else:
            close_tty = False
            output_tty = sys.stdout

        def output_callback(line):
            output_tty.write("%s\n" % line)

        def finish_callback():
            if close_tty:
                output_tty.close()
            self._running = False

        command = self._command
        output_callback("Running %s:" % " ".join(command))
        p = processhandler.ProcessHandlerMixin(command,
            processOutputLine=output_callback,
            onFinish=finish_callback)

        self._running = True
        p.run()
