from django.db import models
from haystack import signals


class TiedModelRealtimeSignalProcessor(signals.RealtimeSignalProcessor):
  pass
