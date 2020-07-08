sap.ui.define([
	"sap/ui/Device",
	"sap/ui/core/mvc/Controller",
	'sap/m/MessageBox',
	"sap/ui/model/json/JSONModel"
], function(Device, Controller, MessageBox, JSONModel) {
	"use strict";


	return Controller.extend("empathygame.controller.Router", {

		onInit: function() {

			this.getView().setModel(new JSONModel({
				isMobile: Device.browser.mobile,
				webSocketText: "",
			}), "view");	

		},
		/**
		 * Helper funciton to build the web socket uri
		 */
		getWssUri: function(route){
			var loc = window.location, new_uri;
			if (loc.protocol === "https:") {
				new_uri = "wss:";
			} else {
				new_uri = "ws:";
			}
			new_uri += "//" + loc.host;
			new_uri += route;
			return new_uri;
		},

		/**
		 * Redirect if not logged in
		
		onBeforeRendering: function() {

			//--Check if we are logged in, otherwise route to login
			if(this.getView().getModel("store").getProperty("/gameId") === ""){
				sap.ui.core.UIComponent.getRouterFor(this).navTo("router");
			}
		}, */

		/**
		 * Vanilla Web Socket Connection Test
		 */
		connectAndCallVanillaWebSocket: function(){
			var that = this;
			var wsUri = this.getWssUri("/api/ws");
			var websocket = new WebSocket(wsUri);
			websocket.onopen = function(evt) { 
				websocket.send("WebSocket rocks");
			};
			websocket.onmessage = function(evt) {
				that.getView().getModel().setProperty("/webSocketText", evt.data);
				websocket.close();
			 };
		},

		/**
		 * Socket.IO Connection Test
		 */
		connectAndCallWebSocket: function(){
			//--To Do...
		},

		/**
		 * Navigation
		 */
		navToLogin: function() {
        	sap.ui.core.UIComponent.getRouterFor(this).navTo("login");
		},

	});

});
