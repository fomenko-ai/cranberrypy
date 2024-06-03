from __future__ import print_function
import json
import os
import sys
import logging

from pydeps import py2depgraph, cli, target
from pydeps.pydeps import externals
from pydeps.depgraph import DepGraph


log = logging.getLogger(__name__)


def _pydeps(trgt, **kw) -> DepGraph:
    if os.getcwd() != trgt.workdir:
        # the tests are calling _pydeps directory
        os.chdir(trgt.workdir)

    dep_graph = py2depgraph.py2dep(trgt, **kw)

    return dep_graph


def pydeps(file_path) -> DepGraph:
    """Entry point for the ``pydeps`` command.

       This function should do all the initial parameter and environment
       munging before calling ``_pydeps`` (so that function has a clean
       execution path).
    """
    sys.setrecursionlimit(10000)
    _args = cli.parse_args([file_path, '--config', 'cranberrypy.ini'])
    _args['curdir'] = os.getcwd()
    inp = target.Target(_args['fname'])
    log.debug("Target: %r", inp)

    if _args.get('output'):
        _args['output'] = os.path.abspath(_args['output'])
    else:
        _args['output'] = os.path.join(
            inp.calling_dir,
            inp.modpath.replace('.', '_') + '.' + _args.get('format', 'svg')
        )

    with inp.chdir_work():
        # log.debug("Current directory: %s", os.getcwd())
        _args['fname'] = inp.fname
        _args['isdir'] = inp.is_dir

        if _args.get('externals'):
            del _args['fname']
            exts = externals(inp, **_args)
            print(json.dumps(exts, indent=4))
            # return exts  # so the tests can assert

        else:
            # this is the call you're looking for :-)
            try:
                return _pydeps(inp, **_args)
            except (OSError, RuntimeError) as cause:
                if log.isEnabledFor(logging.DEBUG):
                    # we only want to log the exception if we're in debug mode
                    log.exception("While running pydeps:")
                cli.error(str(cause))
