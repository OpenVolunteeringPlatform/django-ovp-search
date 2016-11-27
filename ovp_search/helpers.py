from haystack import connection_router, connections
from haystack.inputs import Raw

def is_whoosh_backend():
  backend_alias = connection_router.for_read()

  return connections[backend_alias].__class__.__name__ == "WhooshEngine"


def whoosh_raw(t):
  if is_whoosh_backend():
    return Raw("(\"{}\")".format(t))
  return t
