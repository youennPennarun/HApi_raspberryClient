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
from os.path import expanduser
from requestHandler import RequestHandler, OnHandler

class ServerHandler(threading.Thread):
      logSendedIgnore = ['pi:cpu','pi:notify:sound:volume']
      logMessageIgnore = ['sound:volume:set']
      requests=[]
      listeners=[]
      connected = False
      logger = logging.getLogger('HApi.serverHandler')
      def __init__(self, confPath=None):
          hdlr = logging.FileHandler(expanduser("~")+'/hapi.log')
          formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
          hdlr.setFormatter(formatter)
          self.logger.addHandler(hdlr) 
          self.logger.setLevel(logging.INFO)
          self.logger.info('Initializing player')
          self.connected = False
          threading.Thread.__init__(self)
          args = [];
          appPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'node/app.js');
          args.append('node')
          args.append(appPath)
          if confPath is not None:
             args.append("--conf")
             args.append(confPath);
          self.process = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
          self.on(OnHandler("connected", self.init))
          
      def run(self):
          print("starting serverHandler Thread")
          while self.process.poll() is None:
                lines = self.process.stdout.readline().splitlines()
                #lines = self.process.stdout.readline().splitlines()
                for line in lines:
                    try:
                        data = json.loads(line)
                    except ValueError:
                           self.logger.warning("unable to load " + str(line))
                    else:
                        if data['message'] == "log":
                            if data['type'] == "INFO":
                              self.logger.info("[server_link]:" +data['data'])
                            else:
                              self.logger.warning("[server_link]:" +data['data'])
                        elif data['message'] == "sended":
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
          self.emit(RequestHandler("pi:login", {"name": "rasp1", "ip": self.get_ip_address('wlan0')}))
          self.emit(RequestHandler("pi:ip:set", {'ip':self.get_ip_address('wlan0')}))
          self.emit(RequestHandler("alarm:get", None));
          self.emit(RequestHandler("music:playlist:get", None));
          
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
