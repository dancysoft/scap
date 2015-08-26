# -*- coding: utf-8 -*-
"""
    scap.tmpl
    ~~~~~~~~~
    Scap Config file templating

"""

from jinja2 import Environment, FileSystemLoader
import os
import io

template_path = os.path.join(os.path.curdir(), 'scap', 'templates')

env = Environment(loader=FileSystemLoader(template_path))

class ConfigTemplate:
    """
    :type template: jinja2.Template
    :type context: dict
    """

    template=None

    def __init__(self, output_file, template=None, templates=None, context=None):
        if template != None:
            self.template = env.get_template(name=template_name)
        elif templates != None:
            self.template = env.select_template(names=templates)
        else:
            throw new ValueError('You must provide a value for either [template] or [templates]')
        self.context = context
        self.output_file = output_file

    def render(self, local_vars=None):
        context = self.context.copy()
        """ :type: dict"""
        if local_vars != None:
            context.update(local_vars)

        self.output = self.template.render(context)
        return output

    def write_output_file(self, local_vars=None):
        if not self.output:
            self.render(local_vars=local_vars)

        f = io.open(self.output_file, 'w')
        f.write(self.output.encode('utf8'))
        f.close()
