#!/usr/bin/env python2
"""
Simple example showing a bottom toolbar.
"""
from __future__ import unicode_literals
from prompt_toolkit.shortcuts import get_input
from pygments.token import Token
from context import ShellContext
from pygments.lexers.shell import BashLexer
import ui
import click
import os
import shlex

def main():
    context = ShellContext(os.getcwd())

    def toolbar_token_callback(cli):
        return ui.get_toolbar_tokens(context)

    def prompt_token_callback(cli):
        return ui.get_prompt_tokens(context)

    while True:

        cmd = get_input(get_prompt_tokens=prompt_token_callback,
                         get_bottom_toolbar_tokens=toolbar_token_callback,
                         lexer=BashLexer, style=ui.ScapStyle)

        tokens = BashLexer().get_tokens(cmd)
        for (token, text) in tokens:
            if text is 'cd'
        # lexer = shlex.shlex(cmd)
        tokens = shlex.split(cmd)
        print tokens
        cmd = context.execute(cmd)
        if cmd.value == "exit":
            break

if __name__ == '__main__':
    main()
