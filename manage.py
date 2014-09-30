#!/usr/bin/env python

import subprocess
from alembic.config import main as console_script
from flask.ext.script import Shell, Manager, Command
from application import app
from ext import db


manager = Manager(app)


@manager.command
def clean_pyc():
    """Removes all *.pyc files from the project folder"""
    clean_command = "find . -name *.pyc -delete".split()
    subprocess.call(clean_command)


class ManageMigrations(Command):
    """Manage alembic migrations"""
    capture_all_args = True

    def __init__(self, impl=console_script):
        self.implementation = impl
        super(ManageMigrations, self).__init__()

    def run(self, args):
        import sys, os.path

        prog = '%s %s' % (os.path.basename(sys.argv[0]), sys.argv[1])
        # see if we have the forked version of alembic
        # which accepts prog as an argument to correct the usage string
        try:
            return self.implementation(args, prog)
        except TypeError:
            return self.implementation(args)


manager.add_command('shell', Shell(make_context=lambda:{'app': app, 'db': db}, use_ipython=False))

manager.add_command("migrate", ManageMigrations())


if __name__ == '__main__':
    manager.run()
