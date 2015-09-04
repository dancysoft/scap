"""
Deployment Project environment and path resolution utilities
"""

import io, sys, os
import json

def find_upwards(name, starting_point=None):
    """
    Search the current directory and all parent directories for a given
    filename, returning the first matching path found.
    """
    if starting_point is None:
        starting_point = os.getcwd()

    current = os.path.abspath(starting_point)
    while True:
        if not os.path.exists(current):
            return None

        search = join_path(current, name)
        if os.path.exists(search):
            return search

        parent = os.path.dirname(current)
        if parent == current or parent == "/":
            return None
        current = parent

def _find(name, matchFunc=os.path.isdir, pathlist=sys.path):
    for dirname in pathlist:
        candidate = join_path(dirname, name)
        if matchFunc(candidate):
            return candidate
    return None

def find_dir(name):
    return _find(name, matchFunc=os.path.isdir)

def find_file(name):
    return _find(name, matchFunc=os.path.isfile)

def join_path(*fragments):
    """
    Join several path fragments into a complete, normalized path string.
    Strips leading and trailing slashes from path fragments to avoid an
    unfortunate feature of `os.path.join()` which is described in the python
    documentation for `os.path` as follows:

      "If any component is an absolute path, all previous components are thrown
      away, and joining continues."

      - https://docs.python.org/2/library/os.path.html#os.path.join
    """
    path = []
    i = 0
    for p in fragments:
        if i > 0:
            p = p.strip('\t\r\n').lstrip('/').rstrip('/')
        if (len(p) > 0):
            path.append(p)
        i += 1

    path_str = os.path.join(*path)
    return os.path.normpath(path_str)

class ScapProject(object):
    project_root = None
    scap_dir = None
    project_name = "Scap Project"

    def __init__(self, base_path=None):
        if base_path is None:
            self.scap_dir = find_upwards('scap')
        else:
            self.scap_dir = join_path(base_path, 'scap')

        if self.scap_dir is None:
            raise IOError(errno.ENOENT, 'Unable to locate scap conf directory')

        if not os.path.isdir(self.scap_dir):
            raise IOError(errno.ENOENT, 'Directory not found', self.scap_dir)

        self.project_root = os.path.dirname(self.scap_dir)
        self.project_name = os.path.basename(self.project_root)
        self.template_path = join_path(self.scap_dir, 'templates')
        if not self.project_root in sys.path:
            sys.path.append(self.scap_dir)

        self.command_path = join_path(self.scap_dir, 'cmds')

    def relative_path(self, *args):
        """ build a path relative to the project root """
        return join_path(self.project_root, *args)

    def __repr__(self):
        return json.dumps(vars(self), indent=4)
