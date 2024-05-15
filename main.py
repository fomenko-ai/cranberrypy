from core.adapter.pydeps_lib import pydeps
from core.graph2json import graph2json


graph, filename = pydeps()
graph2json(graph, filename)
