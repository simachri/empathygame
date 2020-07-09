var AppRouter = require("@sap/approuter");

//<--DEV-->
var fs = require('fs');

//--Define routes
process.env.destinations = '[' +
'{"name": "api","url": "http://localhost:8080"}' +
']'; //--Route to local python backend

//--Load development xs-app.json
var xsAppConfig = JSON.parse(fs.readFileSync('./xs-app.json', 'utf8'));
//</--DEV-->

var approuter = new AppRouter();
var options = {
    xsappConfig: xsAppConfig,
    port: process.env.PORT || 3000
};
approuter.start(options);


