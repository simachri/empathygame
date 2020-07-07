var AppRouter = require("@sap/approuter");

var approuter = new AppRouter();
var options = {
    xsappConfig: xsAppConfig,
    port: process.env.PORT || 3000
};
approuter.start(options);


