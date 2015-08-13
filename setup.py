#!/usr/bin/env python
import os
from setuptools import setup, find_packages

long_description = open(
    os.path.join(
        os.path.dirname(__file__),
        'README.rst'
    )
).read()

setup(name='Scap',
      version='1.0',
      description='Wikimedia Deployment Tool',
      long_description=long_description,
      author='Wikimedia Foundation Contributors',
      author_email='bd808@wikimedia.org',
      url='https://doc.wikimedia.org/mw-tools-scap/',
      packages=find_packages('.'),
      entry_points={
        'console_scripts': [
            'scap = scap.scap',
            'iscap = scap.iscap'
        ]
      },
      install_requires=[
        "psutil",
        "netifaces",
        'prompt-toolkit==0.41',
        'tmuxp'
      ],
     )
