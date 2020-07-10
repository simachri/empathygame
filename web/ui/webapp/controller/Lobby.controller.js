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

			var store = this.getOwnerComponent().getModel("store"); 
			var waitingPlayers = store.getProperty("/waitingPlayers");
			
			this.getView().setModel(new JSONModel({
				isMobile: Device.browser.mobile,
				players: waitingPlayers
			}));

			
			//--Update view if player are joining or leaving...
			var eg = store.getProperty("/eg")
			eg.getSocket().on('players_changed', data => {
				MessageToast.show ("Players in lobby changed");
				if(data !== null && data !== undefined){
					store.setProperty("/waitingPlayers", data.players);
					this.getView().setModel(new JSONModel({						
						players: data.players
					}));
				}
			});				
		},

		/**
		 * Redirect if not logged in
		*/
		onBeforeRendering: function() {

			//--Check if we are logged in, otherwise route to login
			//if(this.getView().getModel("store").getProperty("/gameId") === ""){
			//	sap.ui.core.UIComponent.getRouterFor(this).navTo("router");
			//}
			

					

		}, 

		onAfterRendering: function(){

			
			/*
			const model = this.getView().getModel();
			var players = model.getProperty("/players");
			var newPlayers = (players !== null && players !== undefined) ? players.concat({	title: "newFoo"	}) : {	title: "newFoo2"	};
			model.setProperty("/players", newPlayers);

			const model2 = this.getView().getModel("store");
			var players2 = model2.getProperty("/waitingPlayers");
			var newPlayers2 = (players2 !== null && players2 !== undefined) ? players2.concat({	title: "newFoo"	}) : {	title: "newFoo2"	};
			model2.setProperty("/waitingPlayers", newPlayers2);
			*/


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
		}

	});

});
