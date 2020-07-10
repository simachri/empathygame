sap.ui.define([
	"sap/ui/Device",
	"sap/ui/core/mvc/Controller",
	'sap/m/MessageBox',
	"sap/ui/model/json/JSONModel",
	"empathygame/libs/socketio",
    "empathygame/libs/empathygame"
], function(Device, Controller, MessageBox, JSONModel, socketiojs, empathygamejs) {
	"use strict";


	return Controller.extend("empathygame.controller.Password", {

		onInit: function() {

			this.getView().setModel(new JSONModel({
				isMobile: Device.browser.mobile,
			}), "view");	
		},

		/**
		 * Redirect if gameId is not defined yet
		 */
		onBeforeRendering: function() {

			//--Check if we know the game id. Otherwise ask for it.
			if(this.getView().getModel("store").getProperty("/gameId") === ""){
				sap.ui.core.UIComponent.getRouterFor(this).navTo("login");
			}
		},
		
		/**
		 * Function to access game on backend
		 */
		accessGame: function(oEvent) {
			var that = this;

			//--Check if password was given
			if(this.getView().getModel("store").getProperty("/gamePwd") === ""){
				MessageBox.error("Please enter your password");
			}
			else{
				//--Submit data to get access
				var socket = io.connect( {
					'path': '/api/ws/socket.io'
				});
	
				var eg = getEmpathyGame(socket);
				that.getView().getModel("store").setProperty("/eg", eg);
				var gameId = that.getView().getModel("store").getProperty("/gameId");
				var gamePwd	= that.getView().getModel("store").getProperty("/gamePwd");
				var userName = that.getView().getModel("store").getProperty("/userName");
				var userId = that.getView().getModel("store").getProperty("/userId");
				eg.joinGame(gameId, gamePwd, userName,userId);
				//--If join was successful, go to lobby
				eg.getSocket().on('game_joined', data => {
					if(data !== null && data !== undefined){
						var players = data.players;
						that.getView().getModel("store").setProperty("/waitingPlayers", players);
					}                	
                	that.navToLobby();
				});	
				//--If join was not successful, show error message
				eg.getSocket().on('invalid_name_or_pwd', data => {
                	MessageBox.error("The game ID and/or your password is not correct");
            	});	
			}
		},

		/**
		 * Navigation
		 */
		navToLogin: function() {
        	sap.ui.core.UIComponent.getRouterFor(this).navTo("login");
		},
		navToLobby: function() {
        	sap.ui.core.UIComponent.getRouterFor(this).navTo("lobby");
		}
	});
});
