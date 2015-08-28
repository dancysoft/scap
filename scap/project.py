"""
Deployment Project environment and path resolution utilities
"""

import io, sys, os



class DeploymentProject(object):
    project_root = None
    def __init__(self):

        self.scap_dir = self.find_upwards('scap')
        self.project_root = os.path.dirname(self.scap_dir)
        self.project_name = os.path.basename(self.project_root)
        self.template_path = os.path.join(self.scap_dir, 'templates')
        if not self.project_root in sys.path:
            sys.path.append(self.project_root)

    def relative_path(self, name):
        """ resolve a path relative to the project root """
        return os.path.join(self.project_root, name)

    def get_template(self, name):
        os.path.join(self.scap_dir, 'templates', name)

    def find_upwards(self, name):
        """
        Search the current directory and all parents for a given filename,
        returning the first matching path found.
        """
        current = os.path.abspath(os.path.curdir)
        while True:
            search = os.path.join(current, name)
            if os.path.exists(search):
                return search
            parent = os.path.dirname(current)
            if parent == current or parent == "/":
                return None

    def _find(self, path, matchFunc=os.path.isfile):
        for dirname in sys.path:
            candidate = os.path.join(dirname, path)
            if matchFunc(candidate):
                return candidate

        return None

    def find(self, path):
        return self._find(path)

    def findDir(self, path):
        return self._find(path, matchFunc=os.path.isdir)

project = DeploymentProject()

import tmpl
