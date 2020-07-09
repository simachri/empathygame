var AppRouter = require("@sap/approuter");


//--Define routes
process.env.destinations = '[' +
'{"name": "api","url": "https://empathygame-api.cfapps.eu10.hana.ondemand.com"}' +
']'; //--Route to local python backend

var approuter = new AppRouter();
var options = {
    port: process.env.PORT || 3000
};
approuter.start(options);


