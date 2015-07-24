#!/usr/bin/env python3.4
"""
(Python >3.3)

This is an example of how to embed a CommandLineInterface inside an application
that uses the asyncio eventloop. The ``prompt_toolkit`` library will make sure
that when other coroutines are writing to stdout, they write above the prompt,
not destroying the input line.

This example does several things:
    1. It starts a simple coroutine, printing a counter to stdout every second.
    2. It starts a simple input/echo cli loop which reads from stdin.

Very important is the following patch. If you are passing stdin by reference to
other parts of the code, make sure that this patch is applied as early as
possible. ::

    sys.stdout = cli.stdout_proxy()
"""

from __future__ import unicode_literals

from prompt_toolkit.interface import CommandLineInterface
from prompt_toolkit.shortcuts import create_default_application, create_asyncio_eventloop
from prompt_toolkit.application import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.completion import Completion, Completer
from prompt_toolkit.filters import Always
from prompt_toolkit.key_binding.manager import KeyBindingManager
from prompt_toolkit.layout import Window, VSplit, HSplit, Float, FloatContainer
from prompt_toolkit.layout.controls import TokenListControl, FillControl, BufferControl
from prompt_toolkit.layout.dimension import LayoutDimension
from prompt_toolkit.layout.menus import CompletionsMenu
from prompt_toolkit.layout.processors import Processor
from prompt_toolkit.layout.prompt import DefaultPrompt
from prompt_toolkit.layout.toolbars import SystemToolbar, ArgToolbar, CompletionsToolbar, SearchToolbar
from prompt_toolkit.layout.utils import token_list_len
from prompt_toolkit.shortcuts import create_eventloop

from pygments.lexers import PythonLexer
from pygments.style import Style
from pygments.token import Token
from pygments.styles.default import DefaultStyle

import datetime
import time

import asyncio
import sys


loop = asyncio.get_event_loop()

class ScapPrompt(Processor):
    def run(self, cli, buffer, tokens):
        now = datetime.datetime.now()
        before = [
            (Token.Prompt, '%s:%s:%s' % (now.hour, now.minute, now.second)),
            (Token.Prompt, '  hi ')
        ]

        return before + tokens, lambda i: i + token_list_len(before)

    def invalidation_hash(self, cli, buffer):
        return datetime.datetime.now()

class TestCompleter(Completer):
    def get_completions(self, document, complete_event):
        word_before_cursor = document.get_word_before_cursor()

        for i in range(0, 20):
            yield Completion('Completion %i' % i, -len(word_before_cursor))

class TestStyle(Style):
    styles = {
        Token.A: '#000000 bg:#ff0000',
        Token.B: '#000000 bg:#00ff00',
        Token.C: '#000000 bg:#0000ff',
        Token.D: '#000000 bg:#ff00ff',
        Token.E: '#000000 bg:#00ffff',
        Token.F: '#000000 bg:#ffff00',
        Token.HelloWorld: 'bg:#ff00ff',
        Token.Line: 'bg:#000000 #ffffff',

        Token.LineNumber:  'bg:#ffffaa #000000',
        Token.Menu.Completions.Completion.Current: 'bg:#00aaaa #000000',
        Token.Menu.Completions.Completion:         'bg:#008888 #ffffff',
        Token.Menu.Completions.ProgressButton:     'bg:#003333',
        Token.Menu.Completions.ProgressBar:        'bg:#00aaaa',

        Token.Toolbar.Completions:  'bg:#888800 #000000',
        Token.Toolbar.Completions.Arrow: 'bg:#888800 #000000',
        Token.Toolbar.Completions.Completion:  'bg:#aaaa00 #000000',
        Token.Toolbar.Completions.Completion.Current:  'bg:#ffffaa #000000 bold',

        Token.Prompt: 'bg:#00ffff #000000',
        Token.AfterInput: 'bg:#ff44ff #000000',

    }
    styles.update(DefaultStyle.styles)

class Globals(object):
    @property
    def cli(self):
        return self._cli


@asyncio.coroutine
def print_counter():
    """
    Coroutine that prints counters.
    """
    i = 0
    while True:
        #with Globals.cli.patch_stdout_context():
        print('Counter: %i' % i)
        i += 1
        yield from asyncio.sleep(3)


@asyncio.coroutine
def interactive_shell():
    """
    Coroutine that shows the interactive command line.
    """
    # Create an asyncio `EventLoop` object. This is a wrapper around the
    # asyncio loop that can be passed into prompt_toolkit.
    eventloop = create_asyncio_eventloop()

    D = LayoutDimension
    layout = HSplit([

        Window(height=D.exact(1),
                   content=FillControl('-', token=Token.Line)),
        Window(content=BufferControl(
            lexer=PythonLexer,
            input_processors=[ScapPrompt()]
        )),
    ])

    application = Application(layout=layout,
                     buffer=Buffer(completer=TestCompleter()))

    # Create interface.
    cli = CommandLineInterface(
        application=application,
        eventloop=eventloop)
    Globals.cli = cli
    # Patch stdout in something that will always print *above* the prompt when
    # something is written to stdout.
    #sys.stdout = cli.stdout_proxy()

    # Run echo loop. Read text from stdin, and reply it back.
    while True:
        try:
            result = yield from cli.run_async()
            print('You said: "%s"\n' % result.text)
            if result.text == 'exit':
                raise KeyboardInterrupt();
        except (EOFError, KeyboardInterrupt):
            loop.stop()
            print('Qutting event loop. Bye.')
            return


def main():

    sys.stdout.flush()

    asyncio.async(interactive_shell())
    asyncio.async(print_counter())

    loop.run_forever()
    loop.close()


if __name__ == '__main__':
    main()
