import threading
import logging
import time
import subprocess
import os
import sys
import json
import socket
import fcntl
import struct
from requestHandler import RequestHandler, OnHandler

class ServerHandler(threading.Thread):
      logSendedIgnore = ['pi:cpu','pi:notify:sound:volume']
      logMessageIgnore = ['sound:volume:set']
      requests=[]
      listeners=[]
      connected = False
      logger = logging.getLogger('HApi.serverHandler')
      def __init__(self):
          logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
          self.logger.info('Initializing player')
          self.connected = False
          threading.Thread.__init__(self)
          self.process = subprocess.Popen(['node', 
          os.path.join(os.path.dirname(os.path.realpath(__file__)), 'app.js')], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
          self.on(OnHandler("connected", self.init))
          
      def run(self):
          while self.process.poll() is None:
                lines = self.process.stdout.readline().splitlines()
                for line in lines:
                    try:
                        data = json.loads(line)
                    except ValueError:
                           self.logger.warning("unable to load " + str(line))
                    else:
                        if data['message'] == "sended":
                           if data['request'] not in ServerHandler.logSendedIgnore:
                              self.logger.info("sended '"+data['request']+"'")
                        elif data['message'] == 'disconnect':
                             self.logger.info('Disconnected')
                        else:
                             for listener in self.listeners:
                                 if listener.on == data['message']:
                                    if data['message'] not in ServerHandler.logMessageIgnore:
                                       self.logger.info("received response for request "+listener.on)
                                    if listener.callback is not None:
                                       listener.callback(data['data'])
                                    break
                self.process.stdout.flush()
      def init(self, data):
          self.emit(RequestHandler('authentication', {'username': "admin", 'password': "admin"}))
          self.emit(RequestHandler("pi:login"))
          self.emit(RequestHandler("pi:ip:set", {'ip':self.get_ip_address('wlan0')}))
          self.emit(RequestHandler("alarm:get", None));
          
      def get_ip_address(self, ifname):
          s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
          return socket.inet_ntoa(fcntl.ioctl(
                 s.fileno(),
                 0x8915,  # SIOCGIFADDR
                 struct.pack('256s', ifname[:15])
                 )[20:24])
    
      def emit(self,request):
          if self.process.poll() is None:
             if request.responseStr is not None:
                self.requests.append(request)
             if request.data is None :
                  jsonMsg = json.dumps({"message": request.requestStr, "data":{}}, separators=(',',':'))
             else:
                  jsonMsg = json.dumps({"message": request.requestStr, "data":request.data}, separators=(',',':'))
             self.process.stdin.write('%s\n' % jsonMsg)
             self.process.stdin.flush()
          
      def on(self, onHandler):
          self.logger.info("NEW LISTENER: "+onHandler.on)
          self.listeners.append(onHandler)