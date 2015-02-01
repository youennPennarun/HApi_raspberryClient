#!/usr/bin/env python

class RequestHandler:
      def __init__(self, requestStr, data=None, responseStr=None, callback=None):
          self.requestStr = requestStr
          self.data = data
          self.responseStr = responseStr
          self.callback = callback

class OnHandler:
      def __init__(self, on, callback):
          self.on = on
          self.callback = callback