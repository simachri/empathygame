sap.ui.define([
	"sap/ui/Device",
	"sap/ui/core/mvc/Controller",
	"sap/ui/model/json/JSONModel",
	'sap/m/MessageBox',
	'sap/m/MessageToast'
], function(Device, Controller, JSONModel, MessageBox, MessageToast ) {
	"use strict";


	return Controller.extend("empathygame.controller.Lobby", {

		onInit: function() {

			this.getView().setModel(new JSONModel({
				isMobile: Device.browser.mobile,
				webSocketText: "Web Socket not yet Connected.",
				welcomeMessage: ""
			}));	

		},

		/**
		 * Redirect if not logged in
		
		onBeforeRendering: function() {

			//--Check if we are logged in, otherwise route to login
			if(this.getView().getModel("store").getProperty("/gameId") === ""){
				sap.ui.core.UIComponent.getRouterFor(this).navTo("router");
			}
		}, */

		onAfterRendering: function(){
			//--Update view if player are joining or leaving...
			var eg = this.getView().getModel("store").getProperty("/eg");
			eg.getSocket().on('player_joined', data => {
				MessageToast.show ("Player has joined.");
				that.getView().getModel("store").setProperty("waitingPlayers", data);
			});
			eg.getSocket().on('player_left', data => {
				MessageToast.show ("Player has left.");
				that.getView().getModel("store").setProperty("waitingPlayers", data);
			});						
		},

		showData: function(){
			var gameId =   this.getView().getModel("store").getProperty("/gameId");
			var gamePwd =   this.getView().getModel("store").getProperty("/gamePwd");
		},

		/**
		 * Socket.IO Connection Test
		 */
		connectAndCallWebSocket: function(){

			var that = this;

			var socket = io.connect( {
				'path': '/api/ws/socket.io'
			  });

			socket.on('connect', () => {
			// either with send()
			that.getView().getModel().setProperty("/webSocketText", "Connected");
			socket.send('Hello!');

			// or with emit() and custom event names
			socket.emit('salutations', 'Hello!', { 'mr': 'john' }, Uint8Array.from([1, 2, 3, 4]));

			});			

			// handle the event sent with socket.send()
			socket.on('my_response', data => {
				that.getView().getModel().setProperty("/webSocketText", JSON.stringify(data));
			});

			// handle the event sent with socket.emit()
			socket.on('greetings', (elem1, elem2, elem3) => {
			console.log(elem1, elem2, elem3);
			});
		},

		/**
		 * Call hello world test
		 */
		callToGetWelcomeMessage: function(){
			var that = this;
			return jQuery
				.ajax({
				url: "/api/hello",
				method: "GET",
				beforeSend: function(xhr){
					xhr.setRequestHeader('X-Csrf-Token', 'fetch');
				},
				})
				.success(function(json, textStatus, request) {

				// Check if we face mult. repositories
				if(json !== null && json !== undefined){
					// Take first entry as default
					that.getView().getModel().setProperty("/welcomeMessage", json.message);
				} 
				else{
					MessageBox.error("Payload is null or undefined");
				}     
				}).always(function(res, textStatus, request) { that.addXcrfTokenHeader(request)});//--Add new updated X-CSRF-Token 
		},

		/**
		 * Navigation
		 */
		navToLogin: function() {
        	sap.ui.core.UIComponent.getRouterFor(this).navTo("login");
		},

	});

});
