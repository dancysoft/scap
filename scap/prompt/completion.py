from __future__ import unicode_literals

from prompt_toolkit.completion import Completer, Completion
import os
from scap.cli import Application
import scap.main

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
        commands = self._context.commands.copy()
        for app in Application.__subclasses__():
            name = app.__name__
            fullname = app.__module__ + "." + name
            doc = getattr(app, '__doc__', fullname).split("\n")
            if len(doc) > 1:
                doc[0] += " ..."

            display = "%s: %s" % (name, doc[0])
            lname = name.lower()
            if len(words) == 1:
                if lname.startswith(words[0]) or name.startswith(words[0]):
                    yield Completion(name[len(text):], 0, display=display)
            else:
                if words[0].lower() == lname:
                    for arg in getattr(app.main, '_app_arguments', []):
                        skip = False
                        for flag in arg['_flags']:
                             if flag in words:
                                skip = True
                        if skip == True:
                            continue
                        yield Completion(arg['_flags'][0], 0,
                            display="[%s] %s" %("|".join(arg['_flags']), arg['help']))

        for name, cmd in commands.iteritems():
            if name.startswith(words[0]) and len(words) == 1:
                yield Completion(name[len(text):], 0, display=name)
            if words[0] == name and len(words) > 1:
                for subcmd in cmd.subcommands:
                    if subcmd.startswith(words[1]):
                        yield Completion(subcmd[len(text):], 0, display=subcmd)
