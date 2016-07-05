from . import Connector
from .tools import nslist

def get_by_name(ns, name):
    l = nslist(ns, name)
    if len(l)==0:
        raise ValueError("No such worker {0} on {1}".format(name, ns))
    return [Connector(ns, x["data"]["port"]) for x in l]
