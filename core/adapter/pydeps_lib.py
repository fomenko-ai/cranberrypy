from __future__ import print_function
import os
import sys
import logging

from pydeps import py2depgraph, cli, target
from pydeps.depgraph import DepGraph


log = logging.getLogger(__name__)


def _pydeps(trgt, **kw) -> DepGraph:
    if os.getcwd() != trgt.workdir:
        # the tests are calling _pydeps directory
        os.chdir(trgt.workdir)

    dep_graph = py2depgraph.py2dep(trgt, **kw)

    return dep_graph


def pydeps(workdir) -> DepGraph:
    """Entry point for the ``pydeps`` command.

       This function should do all the initial parameter and environment
       munging before calling ``_pydeps`` (so that function has a clean
       execution path).
    """
    sys.setrecursionlimit(10000)
    _args = cli.parse_args([workdir, '--config', 'cranberrypy.ini'])
    _args['curdir'] = os.getcwd()
    inp = target.Target(_args['fname'])
    log.debug("Target: %r", inp)

    with inp.chdir_work():
        # log.debug("Current directory: %s", os.getcwd())
        _args['fname'] = inp.fname
        _args['isdir'] = inp.is_dir

        # this is the call you're looking for :-)
        try:
            return _pydeps(inp, **_args)
        except (OSError, RuntimeError) as cause:
            if log.isEnabledFor(logging.DEBUG):
                # we only want to log the exception if we're in debug mode
                log.exception("While running pydeps:")
            cli.error(str(cause))
