from __future__ import unicode_literals

from prompt_toolkit.completion import Completer, Completion
import os

__all__ = (
    'ScapCompleter',
)


class ScapCompleter(Completer):
    """
    Complete for Path variables.
    :param context: The ShellContext instance that contains the metadata which
                    we need to build the completions.
    """
    def __init__(self, context):
        self._context = context

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        words = text.split(" ")
        for name, cmd in self._context.commands.iteritems():
            if name.startswith(words[0]) and len(words) == 1:
                yield Completion(name[len(text):], 0, display=name)
            if words[0] == name and len(words) > 1:
                for subcmd in cmd.subcommands:
                    if subcmd.startswith(words[1]):
                        yield Completion(subcmd[len(text):], 0, display=subcmd)
