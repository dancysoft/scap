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
from prompt_toolkit.shortcuts import create_default_application, create_asyncio_eventloop, create_eventloop
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
from prompt_toolkit.utils import Callback

from pygments.lexers import PythonLexer
from pygments.style import Style
from pygments.token import Token
from pygments.styles.default import DefaultStyle

import datetime
import time

import asyncio
import sys


class ScapPrompt(Processor):
    def run(self, cli, buffer, tokens):
        now = datetime.datetime.now()
        before = [
            (Token.Prompt, '%s:%s:%s' % (now.hour, now.minute, now.second)),
            (Token.Prompt, '  scap> ')
        ]

        return before + tokens, lambda i: i + token_list_len(before)

    def invalidation_hash(self, cli, buffer):
        return datetime.datetime.now()


class TestCompleter(Completer):
    def get_completions(self, document, complete_event):
        word_before_cursor = document.get_word_before_cursor()

        for i in range(0, 20):
            yield Completion('Completion %i' % i, -len(word_before_cursor))


def main():
    eventloop = create_eventloop()
    done = [False]  # Non local

    #manager = KeyBindingManager(enable_system_bindings=Always())
    D = LayoutDimension
    layout = HSplit([
        Window(content=BufferControl(lexer=PythonLexer, buffer_name='out')),
        Window(height=D.exact(1),
                   content=FillControl('-', token=Token.Line)),
        Window(height=D.exact(2), content=BufferControl(buffer_name='in',
            lexer=PythonLexer,
            input_processors=[ScapPrompt()]
        )),
    ])

    def on_read_start(cli):
        """
        This function is called when we start reading at the input.
        (Actually the start of the read-input event loop.)
        """
        # Following function should be run in the background.
        # We do it by using an executor thread from the `CommandLineInterface`
        # instance.
        def run():
            # Send every second a redraw request.
            while not done[0]:
                time.sleep(1)
                cli.request_redraw()

        cli.eventloop.run_in_executor(run)

    def on_read_end(cli):
        done[0] = True

    default_buffer = Buffer()
    out_buffer = Buffer(is_multiline=True)

    application = Application(layout=layout,
                        on_start = Callback(on_read_start),
                        on_stop = Callback(on_read_end),
                        #key_bindings_registry=manager.registry,
                        buffer = default_buffer,
                        buffers = {'in': default_buffer, 'out': out_buffer},
                        initial_focussed_buffer = 'in',
                        use_alternate_screen = True
                    )

    cli = CommandLineInterface(application=application, eventloop=eventloop)
    #sys.stdout = cli.stdout_proxy()


    while True:
        userinput = cli.run()
        out_buffer.text=out_buffer.text + "\n" + userinput.text
        out_buffer.cursor_position = len(out_buffer.text)
        if userinput.text == "exit":
            break

    eventloop.close()


if __name__ == '__main__':
    main()
