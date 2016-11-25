from haystack import connection_router, connections

def is_whoosh_backend():
  backend_alias = connection_router.for_read()

  return connections[backend_alias].__class__.__name__ == "WhooshEngine"

