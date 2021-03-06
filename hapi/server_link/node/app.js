
var ini = require('node-ini');
var confPath = (process.env.HOME || process.env.HOMEPATH || process.env.USERPROFILE) + '/.hapi_conf';
var ArgumentParser = require('argparse').ArgumentParser;
var parser = new ArgumentParser({
  version: '0.0.1',
  addHelp:true,
  description: ''
});
parser.addArgument(
  [ '-c', '--conf' ],
  {
    help: 'configuration file path'
  }
);
var args = parser.parseArgs();
if(args.conf) {
              confPath=args.conf;
}
var config = ini.parseSync(confPath);

var url = config.Server.url;
var io = require('socket.io-client');
var request = require('request');
var sleep = require('sleep');
function log(str, type) {
	if (!type) {
		type = "INFO";
	}
	try {
		console.log(JSON.stringify({"message":"log", "data": str,"type": type}));
	} catch(e) {
		console.log(str);
	}
}
function tokenConnect () {
         log("connecting to "+url);
    request.post({
        url: url + '/user/login/token',
        form: { username: config.Server.username, password: config.Server.password },
        followAllRedirects: true,
        timeout: 30000
    }, function (err, resp, body) {
       if (err && (err.code == "ETIMEDOUT" || err.code == "ECONNRESET" || err.code == "ENOTFOUND") ) {
          console.log("SERVER_NOT_FOUND");
          sleep.sleep(30);
          tokenConnect ();
          return;
       } else {
            var ok = true,
            	json,
            	token,
            	socket;
            try {
            	json = JSON.parse(body);
            } catch (e) {
            	console.log(e + " on parsing "+ body);
            	ok = false;
            }
            if (ok) {
	            token = json.data.token;
	            socket = io.connect(url, {'query': 'token=' + token });
	            log("ready");
	            socket.on('connect', function () {
	                log("connected");
	                console.log(JSON.stringify({"message": "connected", 'data': {}}));
	            });
	            socket.on('connect_failed', function () {console.log("con f")});
	            socket.on('message', function () {console.log("con f")});
	            socket.on('reconnect_failed', function () {console.log("con f")});
	            socket.on('reconnect', function () {console.log("con f")});
	            socket.on('connecting', function () {console.log("con ing")});
	            socket.on("error", function (error) {
	                if (error.type === "UnauthorizedError" || error.code === "invalid_token") {
	                   socket.disconnect();
	                    tokenConnect();
                        return;
	                } else {
	                console.log(error);
	                }
	            });
	            process.stdin.pipe(require('split')()).on('data', function (line) {
	                json = JSON.parse(line);
	                socket.emit(json.message, json.data);
	                console.log(JSON.stringify({"message": "sended", "request": json.message}));
	            });
	            socket.on('disconnect', function () {
	                console.log(JSON.stringify({"message": "disconnect"}));
/*
          		sleep.sleep(30);
          		tokenConnect ();
*/
	            });
	            socket.on('response:alarm:get', function (data) {
	                console.log(JSON.stringify({"message": "response:alarm:get", "data": data}));
	            });
	            socket.on('alarm:new', function (data) {
	                console.log(JSON.stringify({"message": "alarm:new", "data": data}));
	            });
	            socket.on('alarm:update', function (data) {
	                console.log(JSON.stringify({"message": "alarm:update", "data": data}));
	            });
	            socket.on('alarm:remove', function (data) {
	                console.log(JSON.stringify({"message": "alarm:remove", "data": data}));
	            });
	            socket.on('sound:pause', function () {
	                console.log(JSON.stringify({"message":  "sound:pause", "data": {}}));
	            });
	            socket.on('sound:play', function (data) {
	                console.log(JSON.stringify({"message": "sound:play", "data": data}));
	            });
	            socket.on('sound:resume', function () {
	                console.log(JSON.stringify({"message": "sound:resume", "data": {}}));
	            });
	            socket.on('sound:volume:set', function (data) {
                    log("new volume: "+data.volume);
	                console.log(JSON.stringify({"message": "sound:volume:set","data": data}));
	            });
	            socket.on('sound:volume:get', function() {
	                console.log(JSON.stringify({"message":"sound:volume:get","data":{}}));
	            });
	            socket.on('sound:next', function() {
	                console.log(JSON.stringify({"message":"sound:next","data":{}}));
	            });
	            socket.on('sound:previous', function() {
	                console.log(JSON.stringify({"message":"sound:previous","data": {}}));
	            });
	            socket.on('music:playlist:add', function(data) {
	                console.log(JSON.stringify({"message":"music:playlist:add","data": data}));
	            });
	            socket.on('music:playlist:set', function(data) {
	                console.log(JSON.stringify({"message":"music:playlist:set","data": data}));
	            });
	            socket.on('music:player:next', function(data) {
	                console.log(JSON.stringify({"message":"music:player:next","data": data}));
	            });
	            socket.on('music:player:previous', function(data) {
	                console.log(JSON.stringify({"message":"music:player:previous","data": data}));
	            });
	            socket.on('music:playlist:playing:id', function(data) {
	                console.log(JSON.stringify({"message":"music:playlist:playing:id","data": data}));
	            });
	            socket.on('music:playlist:get', function(data) {
	                console.log(JSON.stringify({"message":"music:playlist:get","data": data}));
	            });
	       } else {
	       	console.log("server error");
          	sleep.sleep(60);
          	tokenConnect ();
	       }
       }
    });
};


tokenConnect();
