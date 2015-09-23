#!/usr/bin/env python2
"""
Interactive deployment shell
"""
from __future__ import unicode_literals
from prompt_toolkit.shortcuts import get_input
from prompt_toolkit.filters import Always
from prompt_toolkit.history import FileHistory
from pygments.token import Token
from scap.prompt.context import ShellContextManager
from scap.prompt.completion import ScapCompleter
from pygments.lexers.shell import BashLexer
#import pexpect
import scap.prompt.ui as ui
#import click
import os
import shlex
import sys
import tmuxp

sys.path.append(os.getcwd())

class LogStreamWrapper(object):
    def __init__(self, stream, delimiter='\r'):
        self.stream = stream
        self.data = []
        self.delimiter = delimiter

    def write(self, data):
        self.data.append(data)
        #self.stream.write(data)
        #self.stream.flush()

    @property
    def num_lines(self):
        return len(self.data)

    @property
    def lastline(self):
        if len(self.data) > 0:
            return self.data[-1]
        else:
            return ""

    def __getattr__(self, attr):
       return getattr(self.stream, attr)


def main():

    #orig_stderr = sys.stderr
    #stderr_wrapper = LogStreamWrapper(orig_stderr)
    #sys.stderr = stderr_wrapper
    with ShellContextManager() as context:
        def toolbar_token_callback(cli):
            tokens = ui.get_toolbar_tokens(context)
            tokens.append((Token.Text, " | "))
            #tokens.append((Token.Text, repr(stderr_wrapper.num_lines)))
            #tokens.append((Token.Text, stderr_wrapper.lastline))
            return tokens

        def prompt_token_callback(cli):
            return ui.get_prompt_tokens(context)

        tmux = ui.setup_tmux()

        if tmux.has_session('iscap'):
            session = tmux.findWhere({'session_name': 'iscap'})
        else:
            print "Error: No tmux session named 'iscap'"
            session = tmux.new_session(session_name="iscap", attach_if_exists=True)
        for pane in tmux._list_panes():
            if pane['pane_id'] == '%1':
                context.output_tty = pane['pane_tty']

        history_file = FileHistory(os.path.expanduser('~/.iscap_history'))
        command_completer = ScapCompleter(context)

        while True:
            cmd = get_input(get_prompt_tokens=prompt_token_callback,
                             get_bottom_toolbar_tokens=toolbar_token_callback,
                             enable_system_bindings=Always(),
                             history=history_file, completer=command_completer,
                             lexer=BashLexer, style=ui.ScapStyle,
                             )
            if len(cmd) > 0:
                try:
                    cmd = context.execute(cmd)
                    if cmd.value == "exit":
                        session.kill_session()
                    elif cmd.value == "detach":
                        tmux.cmd("detach-client")
                    else:
                        try:
                            cmd.start()
                        except:
                            print "Command not found: %s" % cmd[0]
                        #tmux.cmd(cmd.value())
                finally:
                    pass


if __name__ == '__main__':
    main()
