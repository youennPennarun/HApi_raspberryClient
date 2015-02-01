import sys
sys.path.append( "./server_link/" )
from server_link import RequestHandler, OnHandler, ServerHandler
import threading
import psutil
import time

class DataUtils(threading.Thread):
      def __init__(self, serverHandler, config):
          threading.Thread.__init__(self)
          self.setDaemon(True)
          self.serverHandler = serverHandler
          self.sendData = True;
          self.isRunning=True
          try:
              self.cpu_sync_delay= float(config.get('Utils', 'cpu_sync_delay'));
          except ValueError:
              self.cpu_sync_delay= 5
          
      def run(self):
          while(self.isRunning):
                      while(self.sendData):
                                           self.serverHandler.emit(RequestHandler('pi:cpu', {'cpu': psutil.cpu_percent(interval=1)}))
                                           time.sleep(self.cpu_sync_delay)
                      
                                           
          
      
      