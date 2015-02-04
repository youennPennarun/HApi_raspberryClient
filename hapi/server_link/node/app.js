
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
function tokenConnect () {
    request.post({
        url: url + '/user/login/token',
        form: { username: config.Server.username, password: config.Server.password },
        followAllRedirects: true,
        timeout: 30000
    }, function (err, resp, body) {
       if (err && (err.code == "ETIMEDOUT" || err.code == "ECONNRESET") ) {
          console.log("SERVER_NOT_FOUND");
          sleep.sleep(30);
          tokenConnect ();
       } else {
            var json = JSON.parse(body),
                token = json.data.token,
                socket = io.connect(url, {'query': 'token=' + token });
            console.log("ready");
            socket.on('connect', function () {
                console.log("connected");
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
            socket.on('sound:playing:get', function() {
                console.log(JSON.stringify({"message":"sound:playing:get","data": {}}));
            });
       }
    });
};


tokenConnect();